from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from time import sleep
from bs4 import BeautifulSoup
from tqdm import tqdm
from random import randint
import pandas as pd
import re
from datetime import datetime

base_url = "https://www-broadarrowauctions-com.translate.goog/vehicles/results?q%5Bbranch_id_eq%5D=15&q%5Bs%5D%5B0%5D%5Bname_dir%5D=stock.asc&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp"

# options = webdriver.EdgeOptions()
# options.add_argument(f"--app={base_url}")
# options.add_experimental_option(
#     "excludeSwitches", ["enable-automation", "enable-logging"]
# )
# options.add_argument("--inprivate")
# options.add_argument("--allow-running-insecure-content")
# options.add_argument("--ignore-certificate-errors")

# driver = webdriver.Edge(options=options)
# driver.maximize_window()
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # No UI, faster
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--enable-unsafe-swiftshader")
options.add_argument("--disable-images")
driver = webdriver.Chrome(options=options)
driver.get(base_url)

sleep(15)

elements = driver.find_elements(By.CSS_SELECTOR, ".ft-vehicle-item a")
url = elements[0].get_attribute("href")
print(url)
driver.get(
    "https://www-broadarrowauctions-com.translate.goog/vehicles/ch24_r005/2019-chevrolet-corvette-zr1-convertible?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp"
)
soup = BeautifulSoup(driver.page_source, "html.parser")
car_title_raw = soup.find("div", class_="text-top")
if car_title_raw:
    car_title = car_title_raw.find("h1")
    if car_title:
        title = car_title.get_text().strip()
        print(title)

car_price = soup.find("span", id="convert_price")
if car_price:
    price = car_price.get_text().strip()
    print(price)

# sold_status = soup.find("span", id="label")
# if sold_status:
#     sold_status = sold_status.get_text().split()[0]
#     print(sold_status)
sold_status = soup.find("div", class_="price-row mobile")
if sold_status:
    text_s = sold_status.find("span")
    if text_s:
        print(text_s.get_text().strip())
info_raw = soup.select("ul.options-list li")
for info in range(len(info_raw)):
    print(info_raw[info].text)
driver.close()
