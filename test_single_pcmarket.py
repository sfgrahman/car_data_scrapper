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

base_url = "https://www.pcarmarket.com/auction/completed/"

options = webdriver.EdgeOptions()
options.add_argument(f"--app={base_url}")
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", "enable-logging"]
)
options.add_argument("--inprivate")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--ignore-certificate-errors")

driver = webdriver.Edge(options=options)
driver.maximize_window()

driver.get(base_url)
sleep(10)

username = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(driver.find_element(By.ID, "id_username_mod"))
)

password = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(driver.find_element(By.ID, "id_password_mod"))
)
user = "sfgrahman35@gmail.com"
passw = "Mpctest123#"
username.clear()
username.send_keys(user)

password.clear()
password.send_keys(passw)
loginButton = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(driver.find_element(By.ID, "btnLogin"))
)
driver.execute_script("arguments[0].click()", loginButton)
sleep(15)
driver.get("https://www.pcarmarket.com/auction/2015-porsche-cayman-s-5/")
processed_data = {}
soup = BeautifulSoup(driver.page_source, "html.parser")
title = soup.find("h2", class_="blogPostDisplayTitle")
if title:
    processed_data["Title"] = title.text
price = soup.find("span", class_="pushed_bid_amount")
if price:
    processed_data["Price"] = price.text
sold_status = soup.find("span", class_="sold")
if sold_status:
    processed_data["Sold Status"] = sold_status.text
# Locate the <ul> with the desired details
details_list = soup.find("ul", id="auction-details-list")

# Extract key-value pairs
details = {}
if details_list:
    for li in details_list.find_all("li"):
        key = li.find("strong").text.strip()  # Extract the key (text inside <strong>)
        value = li.text.split(":", 1)[1].strip()  # Extract the value after the colon
        details[key] = value

# Print the extracted details
for key, value in details.items():
    processed_data[key] = value

reserve_status = soup.find("span", class_="auctiontype-red")
if reserve_status:
    processed_data["Reserve Status"] = reserve_status.text

seller = soup.find("a", id="memberProfile")
if seller:
    processed_data["Seller"] = seller.text
print(processed_data)
driver.close()
