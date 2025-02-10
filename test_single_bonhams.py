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

# base_url = "https://cars.bonhams.com/auction/25839/lot/10/2018-mercedes-benz-c63-amg-cabriolet-vin-wddwk8gb0jf622015/"
base_url = "https://cars.bonhams.com/auction/30558/preview-lot/5947294/1967-mercedes-benz-250sl-chassis-no-113-043-10-001654/"
options = webdriver.EdgeOptions()
options.add_argument(f"--app={base_url}")
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", "enable-logging"]
)
options.add_argument("--inprivate")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--ignore-certificate-errors")

driver = webdriver.Edge(options=options)
processed_data = []
driver.get(base_url)

sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")
car_title_raw = soup.find("p", class_="sc-47df02c9-3")

# Split the string by "Chassis no." or "VIN."
# split_result = re.split(r"\bChassis no\.|\bVIN\.", car_title_raw.text)
# split_result = [part.strip() for part in split_result if part.strip()]
# print(split_result)
pattern = r"(.*?)(?:Chassis no\. (.*?))?(?:Engine no\. (.*?))?(?:VIN\. (.*?))?$"
extracted_data = [re.match(pattern, item).groups() for item in car_title_raw]
# Convert to readable format
title, chassis, engine, vin = extracted_data[0]
print(title, chassis, engine, vin)
# Locate the target div

car_price = soup.find_all("span", class_="sc-1255b443-0")

if len(car_price) > 1:
    matches = re.findall(r"([€$£])([\d,]+)", car_price[0].text)
    for match in matches:
        currency, price = match  # Unpack tuple
        print(f"Currency: {currency}, Price: {price}")

car_sold = soup.find("div", class_="sc-47df02c9-5")
if car_sold:
    if re.search(r"\bsold\b", car_sold.text, re.IGNORECASE):
        print("Match found: 'Sold'")
else:
    print("No match found")
car_reserve = soup.find("span", class_="sc-a80bc31a-2")
if car_reserve:
    if re.search(r"\bwithout reserve\b", car_reserve.text, re.IGNORECASE):
        print("Match found: 'without reserve'")
else:
    print("No match found")


div = soup.find("div", class_="LotDesc")
if div:
    content_parts = str(div).split("<br/><br/>")
    content_parts_test = [
        str(part).strip() for part in div.decode_contents().split("<br>")
    ]
else:
    print("test")
processed_data = {}
print(content_parts_test[0])
content_first = content_parts_test[0].split("<br/><br/>")[0].split("<br/>")
cleaned_data = [item for item in content_first if item]
for info in range(len(cleaned_data)):
    processed_data[f"info_{info}"] = cleaned_data[info]

i_content = content_parts_test[0].split("<br/><br/>")[1]
# print(i_content)
cleaned_data_i = (
    i_content.replace("*", "").replace("<i>", "").replace("</i>", "").split("<br/>")
)
for info in range(len(cleaned_data_i)):
    processed_data[f"info_i_{info}"] = cleaned_data_i[info]

print(processed_data)
