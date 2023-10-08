#!/usr/bin/env python3


import csv
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import requests
import shutil
import os


user_id = "------------"
password = "-----------"

outputFile = "resultsEbay.csv"
CHROME_PATH = "chromedriver.exe"


def selenium_driver():
    chrome_options = Options()
    
    PATH = CHROME_PATH
    s = Service(PATH)
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument('--log-level 3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--disable-browser-side-navigation')
    

    driver = webdriver.Chrome(service=s, options=chrome_options)
    driver.set_window_size(1920, 1080)
    
    
    return driver





if __name__ == "__main__":
    fh=open("last_errors.txt", "w")
    argvs = sys.argv
    fr = open("numbers.txt", "r")
    img_number = int(fr.readlines()[-1].replace("\n", ""))
    img_number += 1
    fr.close()
    
    start_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime(time.time())) + "\\"
    image_folder = "images\\"

    if os.path.isdir(start_time) == False:
        os.mkdir(start_time)
    if os.path.isdir(start_time + image_folder) == False:
        os.mkdir(start_time + image_folder)

    
    
    try:
        if len(argvs) == 1:
            arg1 = ""
            arg2 = ""
        elif len(argvs) == 2:
            arg1 = ""
            arg2 = argvs[1]
            arg2_obj = time.strptime(arg2, "%b %d, %Y")
        elif len(argvs) == 3:
            arg1 = argvs[1]
            arg2 = argvs[2]
            arg1_obj = time.strptime(arg1, "%b %d, %Y")
            arg2_obj = time.strptime(arg2, "%b %d, %Y")
        else:
            print("Please check arguments.")
            exit()
    except:
        print("Please check arguments.")
        exit()

    with open(start_time + outputFile, "w", newline="") as fw:
        header = ["ItemID", "Title", "Description", "Cost", "Image 1", "Image 2", "Image 3", "Image 4"]
        employee_writer = csv.writer(fw, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(header)
        fw.flush()


        driver = selenium_driver()
        driver.get("https://www.ebay.com/signin/")
        
        input("Please press Enter, if you logged in")

        all_data = []
        
        driver.get("https://www.ebay.com/mye/myebay/v2/purchase")
        input(f"Press enter for fetch order urls:")
        break_number = 0
        while True:
            wait_0 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m-container-items > div.m-order-card"))
            )
            items = driver.find_elements(By.CSS_SELECTOR, "div.m-container-items > div.m-order-card")
            for item in items:
                list=[]
                for i in item.find_elements (By.CLASS_NAME, "primary__item--wrapper"):
                    list.append(i.text)
                d=list[1].split(':')
                print(d)
                #date = item.find_element(By.CLASS_NAME, "primary__item--wrapper").text
                #print(date)
                #date1=date.split(':')
                #print(date1)
                time_obj = time.strptime(d[1], "%b %d, %Y")
                if len(argvs) == 2:
                    if arg2_obj > time_obj:
                        continue

                if len(argvs) == 3:
                    if arg2_obj > time_obj or arg1_obj < time_obj:
                        continue
                
                inner_items = item.find_elements(By.CSS_SELECTOR, "div.m-item-card.m-container-item-layout-row__body")
                for inner_item in inner_items:
                    prod_name = inner_item.find_element(By.CSS_SELECTOR, "a.nav-link").text
                    prod_url = inner_item.find_element(By.CSS_SELECTOR, "a.nav-link").get_attribute("href")
                    prod_id = prod_url.rsplit("/", 1)[1]
                    prod_price = inner_item.find_element(By.CLASS_NAME, "container-item-col__info-item-info-additionalPrice").text
                    print(prod_price)    
                    mini_data = []
                    mini_data.append(prod_name)
                    mini_data.append(prod_url)
                    mini_data.append(prod_id)
                    mini_data.append(prod_price)
                
                    
                    all_data.append(mini_data)
            try:
                nxt_but = driver.find_element(By.CSS_SELECTOR, "button.pagination__next.icon-btn")
                if nxt_but.get_attribute("aria-disabled") != "true":
                    nxt_but.click()
                    input("next page ready?")
                else:
                    break
            except:
                break
        
                

        print("Product URLs fetched")
        print(len(all_data))
        for i, data in enumerate(all_data):
            try:
                print(str(i+1)+"/"+str(len(all_data)))

                prod_url = data[1]
                prod_id = data[2]
                prod_price = data[3]

                prod_desc = ""

                driver.get(prod_url)
                time.sleep(2)
                if data[0] != "":
                    prod_name = data[0]
                else:
                    try:
                        prod_name = driver.find_element(By.CSS_SELECTOR, "h1.x-item-title__mainTitle").text
                    except:
                        try:
                            prod_name = driver.find_element(By.ID, "itemTitle").text
                        except:
                            prod_name = ""

                if len(driver.find_elements(By.CSS_SELECTOR, "a.ppcvip-db")) == 0:
                    read_morebuts = driver.find_elements(By.CSS_SELECTOR, "button.fake-link.fake-link--action")
                    for but in read_morebuts:
                        """social = driver.find_element(By.CSS_SELECTOR, "span.social-dialog-header.medium-text")
                                                                        if social != None:
                                                                            driver.find_element(By.CSS_SELECTOR, "button.icon-btn.lightbox-dialog__close[aria-label='Close the dialog']").click()
                                                                            time.sleep(3)"""
                        if but.text != "Share":
                            but.click()
                    try:
                        dsc = driver.find_element(By.CSS_SELECTOR, "div.x-about-this-item")
                        descs = dsc.find_elements(By.CSS_SELECTOR, "span.ux-textspans")
                        for desc in descs:
                            prod_desc += desc.text
                            prod_desc += "\n"
                    except:
                        pass

                    dt = []
                    dt.append(prod_id)
                    dt.append(prod_name)
                    dt.append(prod_desc)
                    dt.append(prod_price)

                    
                    
                    
                    try:
                        wait_1 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.image.ux-image-carousel-item > img"))
                        )
                    except:
                        pass
                    try:
                        try:
                            photos = driver.find_elements(By.CSS_SELECTOR, "div.image.ux-image-carousel-item > img")
                            if len(photos) == 0:
                                photo = driver.find_element(By.ID, "icImg")
                                photos = [photo]
                        except:
                            photo = driver.find_element(By.ID, "icImg")
                            photos = [photo]
                        

                        for photo in photos:
                            img = photo.get_attribute("src").rsplit("/", 1)[0] + "/s-l500.jpg"
                            r = requests.get(img, stream=True)
                            img_name = str(img_number) + "." + img.rsplit(".", 1)[1]
                            f = open(start_time + image_folder + img_name, "wb")
                            shutil.copyfileobj(r.raw, f)
                            del r
                            f.close()
                            dt.append(img_name)

                            fa = open("numbers.txt", "a")
                            fa.write(str(img_number))
                            fa.write("\n")
                            fa.close()
                            img_number += 1
                    except Exception as e:
                        print(str(e))

                    employee_writer = csv.writer(fw, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    employee_writer.writerow(dt)
                    fw.flush()
                else:
                    read_morebuts = driver.find_elements(By.CSS_SELECTOR, "button.fake-link.fake-link--action")
                    for but in read_morebuts:
                        """social = driver.find_element(By.CSS_SELECTOR, "span.social-dialog-header.medium-text")
                                                                                    if social != None:
                                                                                        driver.find_element(By.CSS_SELECTOR, "button.icon-btn.lightbox-dialog__close[aria-label='Close the dialog']").click()
                                                                                        time.sleep(3)"""
                        if but.text != "Share":
                            but.click()
                    try:
                        dsc = driver.find_element(By.ID, "viTabs_0_is")
                        descs = dsc.find_elements(By.CSS_SELECTOR, "span.ux-textspans")
                        print(descs.text)
                        for desc in descs:
                            prod_desc += desc.text
                            prod_desc += "\n"
                            print(prod_desc)
                    except:
                        pass

                    dt = []
                    dt.append(prod_id)
                    dt.append(prod_name)
                    dt.append(prod_desc)
                    dt.append(prod_price)

                    main_prod_but = driver.find_element(By.CSS_SELECTOR, "a.ppcvip-db").get_attribute("href")
                    driver.get(main_prod_but)
                    time.sleep(2)
                    
                    try:
                        wait_1 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.image.ux-image-carousel-item > img"))
                        )
                    except:
                        pass
                    try:
                        try:
                            photos = driver.find_elements(By.CSS_SELECTOR, "div.image.ux-image-carousel-item > img")
                            if len(photos) == 0:
                                photo = driver.find_element(By.ID, "icImg")
                                photos = [photo]
                        except:
                            photo = driver.find_element(By.ID, "icImg")
                            photos = [photo]
                        

                        for photo in photos:
                            img = photo.get_attribute("src").rsplit("/", 1)[0] + "/s-l500.jpg"
                            r = requests.get(img, stream=True)
                            img_name = str(img_number) + "." + img.rsplit(".", 1)[1]
                            f = open(start_time + image_folder + img_name, "wb")
                            shutil.copyfileobj(r.raw, f)
                            del r
                            f.close()
                            dt.append(img_name)

                            fa = open("numbers.txt", "a")
                            fa.write(str(img_number))
                            fa.write("\n")
                            fa.close()
                            img_number += 1
                    except Exception as e:
                        print(str(e))

                    employee_writer = csv.writer(fw, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    employee_writer.writerow(dt)
                    fw.flush()
            except Exception as e:
                print(f"ERROR on product {str(i)}: {str(e)}")
                fh.write(str(i))
                fh.write("@@@@@\n")


                
                
