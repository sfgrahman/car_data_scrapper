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

base_url = "https://cars.bonhams.com/auction/30406/the-grand-palais/?page=2"

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

scroll_pause_time = 5
max_scroll_attempts = 5
urls = set()
last_height = driver.execute_script("return document.body.scrollHeight")
scroll_attempts = 0

try:
    while scroll_attempts < max_scroll_attempts:

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_pause_time)
        elements = driver.find_elements(By.CSS_SELECTOR, ".sc-aee7ce40-2 a")
        for elem in elements:
            url = elem.get_attribute("href")
            if url and url not in urls:
                print(url)
                # lot_number = re.search(r"/lot/(1\d{2}|2\d{2})/", url)
                # if lot_number:
                urls.add(url)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
        else:
            scroll_attempts = 0  # Reset scroll attempts if content loads
            last_height = new_height
finally:
    # driver.quit()
    # driver.close()
    pass

print(len(urls))
urls_part = []
final_processed_data = {}
i = 0
currency_map = {"€": "EUR", "$": "USD", "£": "GBP", "CHF": "CHF"}
for url in tqdm(urls):
    # if url not in urls_part:
    processed_data = {}
    sleep(randint(5, 10))
    print(url)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    div = soup.find("div", class_="LotDesc")
    if div:
        content_parts = str(div).split("<br/><br/>")

        if len(content_parts) > 0:
            car_title_raw = soup.find("p", class_="sc-47df02c9-3")
            pattern = (
                r"(.*?)(?:Chassis no\. (.*?))?(?:Engine no\. (.*?))?(?:VIN\. (.*?))?$"
            )
            if car_title_raw:
                extracted_data = [
                    re.match(pattern, item).groups() for item in car_title_raw
                ]
                title, chassis, engine, vin = extracted_data[0]
                car_title = title.strip()
                car_chassis = chassis
                car_vin = vin
                engine_no = engine
                processed_data["Title"] = car_title_raw.text
                processed_data["Title_sep"] = car_title
                processed_data["Chassis no."] = car_chassis
                processed_data["VIN."] = car_vin
                processed_data["Engine no."] = engine_no
            else:
                processed_data["Title"] = ""
                processed_data["Title_sep"] = ""
                processed_data["Chassis no."] = ""
                processed_data["VIN."] = ""
                processed_data["Engine no."] = ""
            car_price = soup.find_all("span", class_="sc-1255b443-0")
            if car_price:
                if len(car_price) > 1:
                    matches = re.findall(r"([€$£])([\d,]+)", car_price[0].text)
                    # matches = re.findall(r"\b([A-Z]{3})([\d,]+)", car_price[0].text)
                    currency, low_estimate = matches[0]  # Unpack tuple
                    processed_data["Price"] = ""
                    processed_data["Currency"] = currency_map[currency]
                    processed_data["Low Estimate"] = low_estimate
                    matches = re.findall(r"([€$£])([\d,]+)", car_price[1].text)
                    # matches = re.findall(r"\b([A-Z]{3})([\d,]+)", car_price[0].text)
                    currency, high_estimate = matches[0]  # Unpack tuple
                    processed_data["High Estimate"] = high_estimate
                else:
                    matches = re.findall(r"([€$£])([\d,]+)", car_price[0].text)
                    # matches = re.findall(r"\b([A-Z]{3})([\d,]+)", car_price[0].text)
                    currency, price = matches[0]  # Unpack tuple
                    processed_data["Price"] = price
                    processed_data["Currency"] = currency_map[currency]
                    processed_data["Low Estimate"] = ""
                    processed_data["High Estimate"] = ""
            else:
                processed_data["Price"] = "Estimate: Refer to dept"
            car_sold = soup.find("div", class_="sc-47df02c9-5")
            if car_sold:
                if re.search(r"\bsold\b", car_sold.text, re.IGNORECASE):
                    processed_data["Sold Status"] = "Sold"
                else:
                    processed_data["Sold Status"] = "Unsold"
            else:
                processed_data["Sold Status"] = "Unsold"
            car_reserve = soup.find("span", class_="sc-a80bc31a-2")
            if car_reserve:
                if re.search(r"\bwithout reserve\b", car_reserve.text, re.IGNORECASE):
                    processed_data["Reserve Status"] = "Without Reserve"
                else:
                    processed_data["Reserve Status"] = "With Reserve"
            else:
                processed_data["Reserve Status"] = "With Reserve"

            content_parts_test = [
                str(part).strip() for part in div.decode_contents().split("<br>")
            ]

            content_first = content_parts_test[0].split("<br/><br/>")[0].split("<br/>")
            cleaned_data = [item for item in content_first if item]
            for info in range(len(cleaned_data)):
                processed_data[f"info_{info}"] = cleaned_data[info]
            i_content = content_parts_test[0].split("<br/><br/>")[1]
            cleaned_data_i = (
                i_content.replace("*", "")
                .replace("<i>", "")
                .replace("</i>", "")
                .split("<br/>")
            )
            for info in range(len(cleaned_data_i)):
                processed_data[f"info_i_{info}"] = cleaned_data_i[info]
            processed_data["Event Date"] = "6 February 2025"
            processed_data["Event Location"] = "Paris, The Grand Palais Historique"
            processed_data["listing_URL"] = url
            i += 1
            final_processed_data[i] = processed_data

df = pd.DataFrame.from_dict(final_processed_data, orient="index")
location_column = df.pop("listing_URL")
df["listing_URL"] = location_column
df.to_csv("bonhams/raw/2025/bonhams_2025_feb_paris_upcoming.csv", index=False)
driver.close()
