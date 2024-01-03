from fpdf import FPDF
import os
import cv2
import time

from selenium import webdriver
import requests

import zipfile

NAME = "Komi_san_wa_komyushou"

IM_RAW_W = 836
IM_RAW_H = 1200

IM_W = 210
IM_H = (IM_RAW_H/IM_RAW_W)*210

PREFIX = ""
SUFFIX = ".rawkuma.com.jpg"

BASE_CHAP_URL = "https://rawkuma.com/komi-san-wa-komyushou-desu-chapter-"
TRAGET_DIR_PATH = r"D:/Books/" + NAME + "/"


def get_dl_url(driver, chap_url):
    """
    Visits rawkuma.com using a selenium driver to get the dl url for a specified chapter
    driver: a selenium webdriver
    chap_url: str
    """

    print("Accessing " + chap_url, end = ': ')

    #find element and get url
    try:
        driver.get(chap_url)
        dl_elem = driver.find_element_by_xpath("/html/body/div[3]/div/div[1]/div/article/div[4]/div[2]/span[3]/span[3]/a")
        url = dl_elem.get_attribute("href")
        print("Ok")
    except Exception as e:
        url = ""
        print(e)

    return url

def download_from_url(url, chap_number):

    response = requests.get(url)
    chap_path = TRAGET_DIR_PATH + "downloads/" + NAME + "_chap_" + chap_number + ".zip"

    print("Downloading at " + url, end= ': ')
    print(response.reason)

    with open(chap_path, 'wb') as file:
        file.write(response.content)

    response.close()

    return chap_path

def unzip_to_pdf(chap_zip_path, chap_number):
    with zipfile.ZipFile(chap_zip_path, 'r') as zip_ref:
        zip_ref.extractall(chap_zip_path[:-4])

    os.chdir(chap_zip_path[:-4])

    # PDF setup
    pdf = FPDF('P', 'mm', (IM_W, IM_H))
    pdf.set_top_margin(0)
    pdf.set_left_margin(0)
    pdf.set_auto_page_break(0)
    pdf.set_display_mode('fullpage', 'single')

    num = 0
    image_path = PREFIX + str(num) + SUFFIX 
    while os.path.exists(image_path):
        cv_img = cv2.imread(image_path)

        h = len(cv_img)
        w = len(cv_img[0])

        if h > w:
            pdf.add_page('P')
            if w/h > IM_W/IM_H:
                pdf.image(image_path, w = IM_W)
            else:
                pdf.image(image_path, h = IM_H)

        else:
            pdf.add_page('L')
            if w/h > IM_W/IM_H:
                pdf.image(image_path, h = IM_H)
            else:
                pdf.image(image_path, w = IM_W)
        num = num + 1
        image_path = PREFIX + str(num) + SUFFIX

    print("Generated chapter at " + TRAGET_DIR_PATH + NAME + "_chap_" + chap_number + ".pdf")
    os.chdir("..")
    pdf.output(TRAGET_DIR_PATH + NAME + "_chap_" + chap_number + ".pdf")

if __name__ == "__main__":

    driver = webdriver.Firefox(executable_path = r"C:/Program Files/GeckoDriver/geckodriver.exe")

    if not os.path.exists(TRAGET_DIR_PATH):
        os.mkdir(TRAGET_DIR_PATH)

    if not os.path.exists(TRAGET_DIR_PATH + "downloads/"):
        os.mkdir(TRAGET_DIR_PATH + "downloads/")

    chap_list = [str(i) for i in range(384, 436)]

    for chap in chap_list:
        chap_loc_path = download_from_url(get_dl_url(driver, BASE_CHAP_URL + chap), chap)
        unzip_to_pdf(chap_loc_path, chap)

    driver.quit()

    # urls = get_dl_ids(BASE_CHAP_URL, chap_list)
    # paths = download_from_website(urls, chap_list)

    # unzip_to_pdf(paths)


