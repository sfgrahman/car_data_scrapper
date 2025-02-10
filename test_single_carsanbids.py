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

base_url = "https://carsandbids.com/auctions/37yya4Q0/1995-bmw-m3-coupe"

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
sleep(randint(10, 15))


final_processed_data = {}
processed_data = {}
soup = BeautifulSoup(driver.page_source, "html.parser")
title_element = soup.find(
    "div",
    class_="auction-title",
)
if title_element:
    title = title_element.find("h1")
if title:
    processed_data["Title"] = title.text
else:
    processed_data["Title"] = ""

price = soup.find(
    "span",
    class_="bid-value",
)
if price:
    processed_data["Price"] = float_value = float(
        price.text.replace(",", "").replace("$", "")
    )
else:
    processed_data["Price"] = ""

li_element = soup.find("li", class_="ended")
if li_element:
    car_sold = li_element.find("span", class_="value")
    if car_sold:
        if re.search(r"\bsold\b", car_sold.text, re.IGNORECASE):
            processed_data["Sold Status"] = "Sold"

selling_date_raw = soup.find("span", class_="time-ended")
if selling_date_raw:
    selling_date = selling_date_raw.get_text().strip("on")
    date_obj = datetime.strptime(selling_date.strip(), "%m/%d/%y")
    new_date_str = date_obj.strftime("%m/%d/%Y")
    processed_data["Selling Date"] = new_date_str

auction_heading = soup.find("div", id="auction-jump")
print(auction_heading)
if auction_heading:
    car_reserve = auction_heading.find("span")
    if car_reserve:
        processed_data["Reserve Status"] = car_reserve.text
breadcrumbs = soup.find("div", class_="row auction-breadcrumbs")
year = None
if breadcrumbs:
    ul = breadcrumbs.find("ul")
    if ul:
        last_a_tag = ul.find_all("a")[-1]  # Get the last <a> tag
        year = last_a_tag.text.strip()  # Extract its text
        processed_data["Year"] = year
# Find the quick-facts section
quick_facts = soup.find("div", class_="quick-facts")

data = {}
if quick_facts:
    for dl in quick_facts.find_all("dl"):
        dt_tags = dl.find_all("dt")
        dd_tags = dl.find_all("dd")
        for dt, dd in zip(dt_tags, dd_tags):
            key = dt.text.strip()
            if key == "Seller":
                # Use the second <a> tag inside the Seller <dd>
                second_a_tag = (
                    dd.find_all("a")[1] if len(dd.find_all("a")) > 1 else None
                )
                value = second_a_tag.text.strip() if second_a_tag else None
            elif dd.a:  # If there's a link inside
                value = dd.a.text.strip()
            else:  # Plain text
                value = dd.text.strip()
            data[key] = value
    for key, value in data.items():
        processed_data[key] = value
# processed_data["listing_URL"] = base_url


print(processed_data)

driver.close()
