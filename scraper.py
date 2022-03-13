from curses import REPORT_MOUSE_POSITION
from bs4 import BeautifulSoup
import requests
import shutil
import re
import os
import glob
import json

if not os.path.exists('images'):
    os.makedirs('images')

existing_images = glob.glob('images/*.jpg')

# BASE_URL = "https://www.bellforestproducts.com"
# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# r = requests.get("https://www.bellforestproducts.com/hand-pick", headers=headers).text
# soup = BeautifulSoup(r, 'html.parser')
# contents = soup.find_all(class_="prod_table_row")
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
        text = row.find(class_="prod_name").getText().replace("View Details »", "")
        img_ref = row.findAll("a", href=True)[0]['href']
        product_id = row.find("form").get("id").replace("form_", "")
        front_image_path = get_image(product_id,1)
        back_image_path = get_image(product_id,2)
        data.append({  "text": text,   "front_image": front_image_path,   "back_image": back_image_path})

    
import codecs
with open("site.html", "r", encoding='utf-8') as f:
    text = f.read()
    get_contents(text)
# for elem in soup(text=re.compile(r'Total Results: \d+')):
#     total_num_pages = int(re.search('\d+', elem.parent.text).group(0))
#     break

# for i in range(122):
#     print(f"Page {i+1}")
#     get_contents(i+1)

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

# print("Done")
# print("Total number of products:", len(data))

