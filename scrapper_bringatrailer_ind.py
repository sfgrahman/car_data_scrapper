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


options = webdriver.EdgeOptions()
# options.add_argument(f"--app={base_url}")
options.add_experimental_option(
    "excludeSwitches", ["enable-automation", "enable-logging"]
)
options.add_argument("--inprivate")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--ignore-certificate-errors")

driver = webdriver.Edge(options=options)

file_path = "bringatrailer/bringatrailer_by_year/all_links_not_final.txt"
urls = []
with open(file_path, "r") as file:
    lines = file.readlines()

for l in range(len(lines)):
    print(lines[l])
    urls.append(lines[l].strip())
    # if l > 34:
    #     break
print(len(urls))

chunk_size = len(urls) // 250
# Split manually using slicing
split_arrays = [urls[n : n + chunk_size] for n in range(0, len(urls), chunk_size)]
print(len(split_arrays))
for j in range(189, 200):
    final_processed_data = {}
    i = 0
    currency_map = {"€": "EUR", "$": "USD", "£": "GBP"}
    for url in tqdm(split_arrays[j]):
        processed_data = {}
        print(url)
        driver.get(url)
        sleep(randint(2, 5))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title_status = soup.select_one("h1.post-title").get_text().strip()
        processed_data["Title"] = title_status

        pattern = r"\b\d{4}\b"
        match = re.search(pattern, title_status)
        if match:
            year = match.group(0)
        else:
            year = ""
        processed_data["Year"] = year

        make = soup.find("strong", string="Make")
        if make:
            processed_data["Make"] = make.next_sibling.get_text().strip()
        else:
            processed_data["Make"] = ""
        model_data_raw = soup.find("strong", string="Model")
        if model_data_raw:
            processed_data["Model"] = model_data_raw.next_sibling.get_text().strip()
        else:
            processed_data["Model"] = ""

        selling_price = soup.select_one("span.info-value strong")
        # processed_data["Price"] = selling_price
        if selling_price:
            matches = re.findall(r"([€$£])([\d,]+)", selling_price.get_text().strip())
            currency, price = matches[0]  # Unpack tuple
            processed_data["Price"] = price
            processed_data["Currency"] = currency_map[currency]
        link_chassis_number = soup.select_one("div.item li a")
        if link_chassis_number:
            processed_data["Chassis No."] = link_chassis_number.get_text().strip()
        else:
            processed_data["Chassis No."] = ""

        selling_date_raw = soup.select_one("span.info-value span")
        if selling_date_raw:
            selling_date = selling_date_raw.get_text().strip("on")
            date_obj = datetime.strptime(selling_date.strip(), "%m/%d/%y")
            new_date_str = date_obj.strftime("%m/%d/%Y")
            processed_data["Selling Date"] = new_date_str

        location_raw = soup.find("strong", string="Location")
        if location_raw:
            location_a = location_raw.find_next_sibling("a")
            if location_a:
                processed_data["Location"] = location_a.get_text().strip()
            else:
                processed_data["Location"] = ""
        else:
            processed_data["Location"] = ""

        seller_type_raw = soup.find("strong", string="Private Party or Dealer")
        if seller_type_raw:
            seller_type = seller_type_raw.next_sibling.get_text().strip(":")
            processed_data["Seller Type"] = seller_type

        car_sold = soup.find("span", class_="info-value noborder-tiny")
        if car_sold:
            if re.search(r"\bsold\b", car_sold.text, re.IGNORECASE):
                processed_data["Sold Status"] = "Sold"
        else:
            processed_data["Sold Status"] = "Unsold/Bid"

        reserve_status = soup.select_one("div.item-tag span")
        if reserve_status:
            processed_data["Reserve Status"] = reserve_status.text

        info_raw = soup.select("div.item li")
        for info in range(len(info_raw)):
            if "Chassis:" not in info_raw[info].text:
                processed_data[f"info_{info}"] = info_raw[info].text
        processed_data["listing_URL"] = url
        i += 1
        final_processed_data[i] = processed_data

    df = pd.DataFrame.from_dict(final_processed_data, orient="index")
    file_name = f"bring_new/bring_new_data_final/bringatrailer_new_data_{j}.csv"
    df.to_csv(file_name, index=False)
driver.close()
