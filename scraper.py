from curses import REPORT_MOUSE_POSITION
from bs4 import BeautifulSoup
import requests
import shutil
import re
import os
import glob
import json
import time
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

BASE_URL = "https://www.bellforestproducts.com/"
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

if not os.path.exists('images'):
    os.makedirs('images')

existing_images = glob.glob('images/*.jpg')
df = pd.DataFrame(index=["product_id", "species", "image"])

data = []

def get_image(product_id, index):
    path = f'images/{product_id}_{index}.jpg'
    if path not in existing_images:
        try:
            r = requests.get(f'{BASE_URL}/_includes/hand_picked_images/{product_id}_{index}.jpg', headers=headers, stream=True)
            with open(f'images/{product_id}_{index}.jpg', 'wb') as out_file:
                shutil.copyfileobj(r.raw, out_file)
        except Exception as e:
            print(f'Could not load image for {product_id}_{index} error: {e}')
            pass
        
    else:
        print(f'{path} already exists')
    return f'images/{product_id}_{index}.jpg'

def get_contents(html):
    soup = BeautifulSoup(html, 'html.parser')
    contents = soup.find_all(class_="prod_table_row")
    get_data(contents)

def get_data(contents):
    for row in contents:
        species = row.find(class_="prod_name").getText().replace("View Details »", "").replace(" ", "_").lower()
        img_ref = row.findAll("a", href=True)[0]['href']
        product_id = row.find("form").get("id").replace("form_", "")
        front_image_path = get_image(product_id,1)
        back_image_path = get_image(product_id,2)

        data.append({  "species": species,   "product_id": product_id,   "image": front_image_path})
        data.append({  "species": species,   "product_id": product_id,   "image": back_image_path})


driver.get("https://www.bellforestproducts.com/hand-pick/")
html = driver.page_source
get_contents(html)

while True:
    try:
        driver.find_element(By.XPATH, "//span[.='Next »']").click()
        html = driver.page_source
        get_contents(html)
        time.sleep(1)
    except Exception as e:
        print(e)
        break
driver.quit()

df = pd.DataFrame(data)
print(df.head())
print(df.tail())

df.to_csv("bellforest_data.csv")


print("Done")
# print("Total number of products:", len(data))

