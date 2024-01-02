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
IM_H = IM_RAW_H*IM_RAW_W*210

PREFIX = ""
SUFFIX = ".rawkuma.com.jpg"

BASE_CHAP_URL = "https://rawkuma.com/komi-san-wa-komyushou-desu-chapter-"

def get_dl_ids(base_chap_url, chap_list):
    """
    Visits rawkuma.com using a selenium driver for every chapter number in chap_list. 
    Then the download button is located and analysed to retrieve the dl url
    base_chap_url: str
    chap_list: [str]
    """
    driver = webdriver.Firefox(executable_path = "geckodriverv033/geckodriver.exe")

    dl_urls = []

    for chap in chap_list:

        print("Accessing chapter " + chap, end = ': ')

        #find element and get url
        try:
            driver.get(base_chap_url + chap)
            dl_elem = driver.find_element_by_xpath("/html/body/div[3]/div/div[1]/div/article/div[4]/div[2]/span[3]/span[3]/a")
            dl_urls.append(dl_elem.get_attribute("href"))
        except Exception as e:
            print(e)

        print("dl url obtained")

    driver.quit()

    return dl_urls

def download_from_website(url_list, chap_list):

    paths = []

    for url, chap in zip(url_list, chap_list):
        response = requests.get(url)
        chap_path = NAME + "_chap_" + chap + ".zip"

        print("Downloading at " + url, end= ': ')
        print(response.reason)
        response.close()

        with open(chap_path, 'wb') as file:
            file.write(response.content)
        time.sleep(5)

        paths.append(chap_path)

    return paths

def unzip_to_pdf(paths):
    for path in paths:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(path[:-4])

        os.chdir(path[:-4])

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

        # Make new directory in books if not created

        print("Generated chapter at " + "D:/Books/" + NAME + "/" + path[:-4] + ".pdf")
        os.chdir('..')
        pdf.output(r"D:/Books/" + NAME + "/" + path[:-4] + ".pdf")

if __name__ == "__main__":

    if not os.path.exists(r"D:/Books/" + NAME):
            os.mkdir(r"D:/Books/" + NAME)

    chap_list = []

    for i in range(160,436):
        chap_list.append(f"{i:02}")

    urls = get_dl_ids(BASE_CHAP_URL, chap_list)

    os.chdir("./downloads")
    paths = download_from_website(urls, chap_list)

    unzip_to_pdf(paths)


