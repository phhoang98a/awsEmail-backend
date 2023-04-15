from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from decouple import config
import pandas as pd


def extract_email(post_url):
    print("davao")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    LINKEDIN_USERNAME = config('LINKEDIN_USERNAME')
    LINKEDIN_PASSWORD = config('LINKEDIN_PASSWORD')
    driver.get("https://www.linkedin.com/")

    username = driver.find_element(By.NAME, "session_key")
    username.send_keys(LINKEDIN_USERNAME)

    password = driver.find_element(By.NAME, "session_password")
    password.send_keys(LINKEDIN_PASSWORD)

    sign_in_button = driver.find_element(By.XPATH, "//*[@type='submit']")
    sign_in_button.click()

    driver.get(post_url)

    try:
        load_more_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "comments-comments-list__load-more-comments-button")))
        while True:
            load_more_button.click()
            sleep(1)
            try:
                load_more_button = driver.find_element(
                    By.CLASS_NAME, "comments-comments-list__load-more-comments-button"
                )
            except:
                print("All comments have been displayed!")
                print("everything is Ok now , come and see it")
                break
    except Exception as e:
        print("All comments are displaying already!")

    list = driver.find_elements(
        By.XPATH, '//a [contains(@href,"mailto")][@href]')
    emails = []
    for i in list:
        email = i.get_attribute("href")
        emails.append(email.split(":")[1])

    return emails
