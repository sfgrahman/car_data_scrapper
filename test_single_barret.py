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

base_url = "https://www.barrett-jackson.com/scottsdale-2019/docket/vehicle/2008-bentley-continental-gtc-convertible-224928"

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
child_element = driver.find_element(By.XPATH, "//*[@id='header']/div/div[2]/button[2]")
actions = ActionChains(driver)
actions.move_to_element(child_element).perform()
sleep(5)
username = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(driver.find_element(By.ID, "email-login-desktop"))
)

password = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(driver.find_element(By.ID, "password-login-desktop"))
)
user = "sfgrahman35@gmail.com"
passw = "Btest123#"
username.clear()
username.send_keys(user)

password.clear()
password.send_keys(passw)
loginButton = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable(
        driver.find_element(By.XPATH, "//*[@id='header']/div/div[4]/div/form/button")
    )
)
driver.execute_script("arguments[0].click()", loginButton)
sleep(15)


soup = BeautifulSoup(driver.page_source, "html.parser")

processed_data = {}
title = soup.find("h1", class_="mb-5")
processed_data["Title"] = title.text

div = soup.find_all(
    "div",
    class_="rounded-lg pb-1 px-2 border border-gray-700 bg-gray-50/20 w-fit inline-block mr-3 mb-3",
)
print(div)
print(len(div))
price_span = (
    div[0].find("span", class_="font-extrabold text-xs leading-4 text-gray-bolder")
    if div
    else None
)
price = price_span.text.strip() if price_span else ""
processed_data["Price"] = price
reserve_span = (
    div[1].find("span", class_="font-medium text-xs leading-4 text-gray-bolder")
    if div
    else None
)
reserve_status = reserve_span.text.strip() if reserve_span else ""
processed_data["Reserve Status"] = reserve_status
sold_span = (
    div[3].find("span", class_="font-extrabold text-xs leading-4 text-gray-bolder")
    if div
    else None
)
sold_status = sold_span.text.strip() if sold_span else ""
processed_data["Sold Status"] = sold_status
event_span = (
    div[4].find("span", class_="font-medium text-xs leading-4 text-gray-bolder")
    if div
    else None
)
event_status = event_span.text.strip() if event_span else ""
processed_data["Event Date"] = event_status
location_span = (
    div[5].find("span", class_="font-extrabold text-xs leading-4 text-gray-bolder")
    if div
    else None
)
location_status = location_span.text.strip() if location_span else ""
processed_data["Location"] = location_status
div = soup.find_all(
    "div",
    class_="w-full flex flex-col justify-center items-center gap-y-1 text-center lg:col-span-1",
)
details = []
for d in div:
    data_span = (
        d.find("span", class_="font-semibold text-lg leading-6 text-white")
        if div
        else None
    )
    data_text = data_span.text.strip() if data_span else ""
    details.append(data_text)

key_names = [
    "Year",
    "Make",
    "Model",
    "Style",
    "Cylinders",
    "Transmission",
    "Engine Size",
    "Exterior Color",
    "Interior Color",
    "Vin",
]
paired_list = list(zip(key_names, details))
processed_data.update(dict(paired_list))
print(processed_data)
driver.close()
