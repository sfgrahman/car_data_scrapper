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

base_url = [
    "https://rmsothebys.com/auctions/az25/lots/#?SortBy=Default&CategoryTag=All%20Motor%20Vehicles&page=3&pageSize=40",
]

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
urls = []

for url in base_url:
    driver.get(url)
    sleep(randint(3, 7))
    products = driver.find_elements(By.CSS_SELECTOR, ".search-result a")
    # link = products[0].get_attribute("href")
    # print(link)
    # print(len(products))
    count_url = []
    for product in products:
        link = product.get_attribute("href")
        if link != "" and link not in urls:
            urls.append(link)
            count_url.append(link)
    print(f"{url}---{len(count_url)}")
# driver.close()

print(len(urls))
final_processed_data = {}
i = 0
for url in tqdm(urls):
    processed_data = {}
    sleep(randint(3, 7))
    print(url)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    car_title_raw = soup.find("h1", class_="heading-title")
    if car_title_raw:
        car_title = car_title_raw.get_text().strip()
    else:
        car_title = ""
    processed_data["Title"] = car_title
    gal_details = soup.find("div", class_="lot-gallery-container")
    chassis_no = None
    location = None
    if gal_details:
        ch_details = gal_details.find_all("div", class_="body-text--copy")
        for section in ch_details:
            label = section.find(
                "div", class_="idlabel"
            ).text.strip()  # Extract the label
            data_value = section.find(
                "div", class_="iddata"
            ).text.strip()  # Extract the data
            if label == "Chassis No.":
                chassis_no = data_value
                processed_data["Chassis No"] = chassis_no
            elif label == "Location":
                location = data_value.split("|")[-1].strip()
                processed_data["Location"] = location

    car_details = soup.find_all("div", class_="lot-header--detail-container")
    for data in car_details:
        price_data = data.find("div", class_="ng-scope")
        if price_data:
            price = price_data.get_text().strip()
        else:
            price = ""
        processed_data["Price"] = price
        info_raw = soup.select("ul.list-bullets li")
        for info in range(len(info_raw)):
            processed_data[f"info_{info}"] = info_raw[info].text
    processed_data["Event Date"] = "24 January 2025"
    processed_data["listing_URL"] = url
    i += 1
    final_processed_data[i] = processed_data
    # print(final_processed_data)
df = pd.DataFrame.from_dict(final_processed_data, orient="index")
location_column = df.pop("listing_URL")
df["listing_URL"] = location_column
df.to_csv("rmsothebys/raw/2025/rmsothebys_2025_ari_3.csv", index=False)
driver.close()
