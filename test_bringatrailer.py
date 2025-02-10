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

base_url = "https://bringatrailer.com/auctions/results/?category=415&category=434&category=492&category=491&category=433&yearFrom=1950&yearTo=1990&timeFrame=5Y"

# options = webdriver.EdgeOptions()
# options.add_argument(f"--app={base_url}")
# options.add_experimental_option(
#     "excludeSwitches", ["enable-automation", "enable-logging"]
# )
# options.add_argument("--inprivate")
# options.add_argument("--allow-running-insecure-content")
# options.add_argument("--ignore-certificate-errors")

# driver = webdriver.Edge(options=options)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # No UI, faster
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--enable-unsafe-swiftshader")
options.add_argument("--disable-images")
driver = webdriver.Chrome(options=options)
processed_data = []
driver.get(base_url)
sleep(10)
i = 0
# urls = set()
# file_path = "bringatrailer_new.txt"
# file_path_not = "bringatrailer_new_not_present.txt"
file_path_not = "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1950_1990_25.txt"
file_list = [
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1950_1990.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1950_1990_1.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1950_1990_2.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1990_2010.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1990_2010_1.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_1990_2010_2.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_2010_2025.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_2010_2025_1.txt",
   "bringatrailer/bringatrailer_by_year/bringatrailer_by_year_2010_2025_2.txt",
]

urls = []
for file_l in file_list:
    with open(file_l, "r") as file:
        lines = file.readlines()
        for l in range(len(lines)):
            urls.append(lines[l].strip())

print(len(urls))
while True:
    products = driver.find_elements(By.CSS_SELECTOR, ".listings-container a")
    print(f"page_{i}: {len(products)}")
    for product in products:
        url = product.get_attribute("href")
        if url and url not in urls:
            urls.append(url)
            with open(file_path_not, "a") as file:
                file.write(url + "\n")
    print(f"Total length: {len(urls)}")
    try:
        next_button = WebDriverWait(driver, 300).until(
            EC.element_to_be_clickable(
                driver.find_element(By.XPATH, "//*[contains(text(), 'Show More')]")
            )
        )
        driver.execute_script("arguments[0].click();", next_button)
        # sleep(randint(10, 15))
        i += 1
        # if i == 550:
        # break
    except NoSuchElementException as e:
        break


print(len(urls))
driver.close()
