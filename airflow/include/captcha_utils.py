import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import requests
import logging
import time
import os
from google.cloud import vision
import numpy as np
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize Google Cloud Vision client
def get_vision_client():
    global vision_client
    if vision_client is not None:
        return vision_client
        
    try:
        # Check if credentials file exists
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds_path or not os.path.exists(creds_path):
            logging.error(f"Google Cloud credentials not found at {creds_path}")
            return None
            
        vision_client = vision.ImageAnnotatorClient()
        logging.info("Successfully initialized Google Cloud Vision client")
        return vision_client
    except Exception as e:
        logging.error(f"Could not initialize Google Cloud Vision client: {e}")
        return None

vision_client = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# OCR configuration
TESSERACT_CONFIG = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Common OCR corrections
OCR_REPLACEMENTS = {
    'O': '0',  # Letter O to number 0
    'I': '1',  # Letter I to number 1
    'S': '5',  # Letter S to number 5
    'Z': '2',  # Letter Z to number 2
    'B': '8',  # Letter B to number 8
    'G': '6',  # Letter G to number 6
    'T': '7',  # Letter T to number 7
    'Q': '0'   # Letter Q to number 0
}

# Selenium timeouts
WAIT_TIMEOUT = 10  # Seconds to wait for elements
CAPTCHA_LOAD_DELAY = 2  # Seconds to wait for CAPTCHA to load
VALIDATION_DELAY = 3  # Seconds to wait for CAPTCHA validation from each method

# OCR configuration
PSM_MODES = [6, 7, 8, 13]  # Different Tesseract Page Segmentation Modes
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence score to consider a result
MAX_RESULTS = 3  # Maximum number of results to consider from each method

# Image processing parameters
DENOISE_KERNEL = 3
MORPH_KERNEL = np.ones((2,2), np.uint8)
CONTRAST_FACTORS = [1.5, 2.0, 2.5]
BRIGHTNESS_FACTORS = [0.8, 1.0, 1.2]

def enhance_image(img):
    """Apply various image enhancement techniques to improve OCR.
    
    Args:
        img: PIL Image object to enhance
        
    Returns:
        PIL Image: Enhanced image
    """
    try:
        # Convert to grayscale
        img = img.convert('L')
        
        # Apply contrast enhancement
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # Apply sharpness enhancement
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)
        
        # Apply brightness enhancement
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)
        
        # Apply Gaussian blur to reduce noise
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Apply threshold to make text more prominent
        img = img.point(lambda x: 0 if x < 128 else 255, '1')
        
        # Convert back to RGB
        img = img.convert('RGB')
        
        return img
        
    except Exception as e:
        logging.error(f"Error enhancing image: {e}")
        return None
    for contrast in CONTRAST_FACTORS:
        for brightness in BRIGHTNESS_FACTORS:
            adjusted = cv2.convertScaleAbs(denoised, alpha=contrast, beta=brightness*50)
            
            # Apply threshold
            _, thresh = cv2.threshold(adjusted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations
            opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, MORPH_KERNEL)
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, MORPH_KERNEL)
            
            # Edge enhancement
            edges = cv2.Canny(closed, 100, 200)
            enhanced = cv2.addWeighted(closed, 0.8, edges, 0.2, 0)
            
            enhanced_images.append(enhanced)
    
    return enhanced_images

def process_captcha(driver, img_xpath, input_xpath=None):
    """Process CAPTCHA using Google Cloud Vision API with fallback to Tesseract OCR.
    
    Args:
        driver: Selenium WebDriver instance
        img_xpath: XPath to locate the CAPTCHA image
        input_xpath: Optional XPath for the CAPTCHA input field
    
    Returns:
        str: Recognized CAPTCHA text, or empty string on error
    """
    try:
        # Find CAPTCHA image
        captcha_img = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, img_xpath))
        )
        
        # Get image source and screenshot as fallback
        img_src = captcha_img.get_attribute('src')
        if not img_src:
            logging.error("Could not get CAPTCHA image source")
            return ""
            
        # Save screenshot for debugging
        driver.save_screenshot('/tmp/captcha_page.png')
        
        # Convert image to bytes
        try:
            if 'base64' in img_src:
                try:
                    # Get raw base64 data after the comma
                    base64_data = img_src.split(',', 1)[1] if ',' in img_src else img_src
                    base64_data = base64_data.strip()
                    
                    # Remove any URL-safe chars and add padding
                    base64_data = base64_data.replace('-', '+').replace('_', '/')
                    missing_padding = len(base64_data) % 4
                    if missing_padding:
                        base64_data += '=' * (4 - missing_padding)
                        
                    # Decode base64
                    img_data = base64.b64decode(base64_data)
                    
                    # Try to open image
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Save original for debugging
                    img.save('/tmp/original_captcha.png')
                    
                    # Enhance image
                    enhanced_img = enhance_image(img)
                    if enhanced_img is None:
                        logging.error("Failed to enhance image")
                        return ""
                    
                    # Save enhanced image for debugging
                    enhanced_img.save('/tmp/enhanced_captcha.png')
                    
                    # Convert to bytes
                    img_bytes = io.BytesIO()
                    enhanced_img.save(img_bytes, format='PNG', optimize=True)
                    img_data = img_bytes.getvalue()
                except Exception as e:
                    logging.error(f"Base64 decoding error: {e}")
                    logging.debug(f"Base64 string length: {len(img_src)}")
                    return ""
            else:
                # Handle URL images
                response = requests.get(img_src)
                if response.status_code == 200:
                    img_data = response.content
                else:
                    logging.error(f"Failed to download CAPTCHA image: {response.status_code}")
                    return ""
            
            # Try Google Cloud Vision API first
            if vision_client:
                try:
                    image = vision.Image(content=img_data)
                    response = vision_client.text_detection(image=image)
                    texts = response.text_annotations
                    
                    if texts:
                        # Get first result
                        text = texts[0].description.strip()
                        text = ''.join(c for c in text if c.isalnum())
                        text = text.upper()
                        
                        # Apply OCR corrections
                        for old, new in OCR_REPLACEMENTS.items():
                            text = text.replace(old, new)
                        
                        logging.info(f"Google Vision API result: {text}")
                        return text
                    else:
                        logging.warning("No text found by Google Vision API")
                except Exception as e:
                    logging.error(f"Error using Google Vision API: {e}")
            
            # Fallback to Tesseract OCR
            logging.info("Falling back to Tesseract OCR")
            img = Image.open(io.BytesIO(img_data))
            
            # Image preprocessing
            img = img.convert('L')  # Convert to grayscale
            img = ImageEnhance.Contrast(img).enhance(2)  # Increase contrast
            img = ImageEnhance.Sharpness(img).enhance(2)  # Increase sharpness
            img = img.filter(ImageFilter.MedianFilter(size=3))  # Remove noise
            img = img.point(lambda x: 0 if x < 140 else 255)  # Threshold
            
            # Use Tesseract OCR
            text = pytesseract.image_to_string(
                img,
                config=TESSERACT_CONFIG
            ).strip()
            
            # Clean and format text
            text = ''.join(c for c in text if c.isalnum())
            text = text.upper()
            
            # Apply OCR corrections
            for old, new in OCR_REPLACEMENTS.items():
                text = text.replace(old, new)
            
            logging.info(f"Tesseract OCR result: {text}")
            return text
            
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return ""
            
    except Exception as e:
        logging.error(f"Error in CAPTCHA processing: {e}")
        return ""

def refresh_captcha(driver, refresh_button_xpath=None):
    """
    Attempt to refresh the CAPTCHA image.
    
    Args:
        driver: Selenium WebDriver instance
        refresh_button_xpath: XPath to the CAPTCHA refresh button (optional)
    
    Returns:
        bool: True if refresh was successful, False otherwise
    """
    try:
        if refresh_button_xpath:
            # Try clicking the refresh button if provided
            refresh_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, refresh_button_xpath))
            )
            refresh_btn.click()
        else:
            # Try common refresh button selectors
            selectors = [
                "//img[contains(@src, 'captcha')]/..//a[contains(@href, 'refresh') or contains(@onclick, 'refresh')]",
                "//img[contains(@src, 'captcha')]/..//img[contains(@src, 'refresh')]",
                "//img[contains(@src, 'captcha')]/..//button[contains(., 'refresh') or contains(., 'Refresh')]"
            ]
            
            for selector in selectors:
                try:
                    refresh_btn = driver.find_element(By.XPATH, selector)
                    if refresh_btn.is_displayed() and refresh_btn.is_enabled():
                        refresh_btn.click()
                        time.sleep(1)  # Wait for new CAPTCHA to load
                        return True
                except:
                    continue
        
        return False
    except Exception as e:
        print(f"Error refreshing CAPTCHA: {e}")
        return False

def handle_captcha_automatically(driver, captcha_image_xpath, captcha_input_xpath, 
                           search_button_xpath=None, refresh_button_xpath=None, max_attempts=3):
    """Handle CAPTCHA validation automatically.
    
    Args:
        driver: Selenium WebDriver instance
        captcha_image_xpath: XPath to the CAPTCHA image
        captcha_input_xpath: XPath to the CAPTCHA input field
        search_button_xpath: Optional XPath to the search/submit button
        refresh_button_xpath: Optional XPath to the refresh button
        max_attempts: Maximum number of attempts to solve CAPTCHA
    
    Returns:
        bool: True if CAPTCHA was successfully validated, False otherwise
    """
    attempts = 0
    while attempts < max_attempts:
        # Process CAPTCHA
        captcha_text = process_captcha(driver, captcha_image_xpath)
        if not captcha_text:
            logging.warning("Failed to process CAPTCHA")
            if not refresh_captcha(driver, refresh_button_xpath):
                break
            attempts += 1
            continue
        
        # Enter CAPTCHA text
        try:
            input_field = driver.find_element(By.XPATH, captcha_input_xpath)
            input_field.clear()
            input_field.send_keys(captcha_text)
        except Exception as e:
            logging.error(f"Error entering CAPTCHA text: {e}")
            if not refresh_captcha(driver, refresh_button_xpath):
                break
            attempts += 1
            continue
        
        # Click search button if provided
        if search_button_xpath:
            try:
                search_button = driver.find_element(By.XPATH, search_button_xpath)
                search_button.click()
            except Exception as e:
                logging.error(f"Error clicking search button: {e}")
                if not refresh_captcha(driver, refresh_button_xpath):
                    break
                attempts += 1
                continue
        
        # Wait for validation
        time.sleep(VALIDATION_DELAY)
        
        # Check for invalid CAPTCHA message
        error_messages = driver.find_elements(By.XPATH, "//div[contains(text(), 'Invalid CAPTCHA')]")
        if not error_messages:
            return True
        
        logging.warning(f"CAPTCHA validation failed. Attempt {attempts + 1}/{max_attempts}")
        if not refresh_captcha(driver, refresh_button_xpath):
            break
        attempts += 1
    
    logging.error("CAPTCHA validation failed after max attempts")
    return False

def check_captcha_and_reload(driver, xpath_image, xpath_input_text, search_button_xpath=None):
    """Check if CAPTCHA validation failed and reload if necessary.
    
    Args:
        driver: Selenium WebDriver instance
        xpath_image: XPath to the CAPTCHA image
        xpath_input_text: XPath to the CAPTCHA input field
        search_button_xpath: Optional XPath to the search button
    
    Returns:
        bool: True if CAPTCHA validation successful, False otherwise
    """
    # Use the main CAPTCHA handling function
    return handle_captcha_automatically(
        driver=driver,
        captcha_image_xpath=xpath_image,
        captcha_input_xpath=xpath_input_text,
        search_button_xpath=search_button_xpath,
        max_attempts=3
    )
