from Utils import SeleniumScrappingUtils
from PIL import Image, ImageFilter
from pytesseract import image_to_string 
import numpy
from scipy.ndimage.filters import gaussian_filter
import os
from selenium.webdriver.common.by import By

th1 = 140
th2 = 140 # threshold after blurring 
sig = 1.5 

def captcha(browser,captcha_image_xpath):
    captcha_image_element = SeleniumScrappingUtils.get_page_element(browser,captcha_image_xpath)
    SeleniumScrappingUtils.save_image_as_png(captcha_image_element)
    original = Image.open('captcha_image.png')
    original.save("original.png")
    black_and_white =original.convert("L") 
    black_and_white.save("black_and_white.png")

    first_threshold = black_and_white.point(lambda p: p > th1 and 255)
    first_threshold.save("first_threshold.png")


    blur=numpy.array(first_threshold) #create an image array
    blurred = gaussian_filter(blur, sigma=sig)
    blurred = Image.fromarray(blurred)
    blurred.save("blurred.png")

    final = blurred.point(lambda p: p > th2 and 255)
    final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    final = final.filter(ImageFilter.SHARPEN)
    final.save("final.png")

    #         remove images 
    os.remove("black_and_white.png")
    os.remove("first_threshold.png")
    os.remove("blurred.png")
    os.remove("original.png")


    config = ("-l eng --oem 3 --psm 11")
    captcha_text = image_to_string(Image.open('final.png'), lang = "eng",config=config)
    return captcha_text
