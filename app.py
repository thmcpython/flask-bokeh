import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template
import time
import selenium
import pandas as pd
from selenium import webdriver
import chromedriver_binary # Importing this exports chrome path to $PATH, below code will fail without this import
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

GOOGLE_CHROME_PATH = os.getenv('GOOGLE_CHROME_BIN')
chrome_bin = os.environ.get('GOOGLE_CHROME_SHIM', None)
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

chrome_serv=Service(CHROMEDRIVER_PATH)
chrome_options = Options()
chrome_options.binary_location = chrome_bin
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
# chrome_options.binary_location = GOOGLE_CHROME_PATH
chrome_options.add_argument("--headless") # These chrome options are included in the new buildpack by default
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--no-sandbox")
# CHROMEDRIVER_PATH = r"C:\Users\timtr\Documents\Coding\Dev_Tools\chromedriver.exe"   #The random r before the path converts it to a raw string

# internetdriver = webdriver.Chrome(service=CHROMEDRIVER_PATH)

internetdriver = webdriver.Chrome(service=chrome_serv, options=chrome_options)
# internetdriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) # This might also work
# internetdriver = webdriver.Chrome(CHROMEDRIVER_PATH, chrome_options=chrome_options)

@app.route('/')
def test():
    URL = "https://spotwx.com/products/grib_index.php?model=nam_awphys&lat=49.81637&lon=-123.33601&tz=America/Vancouver&display=table"
    list = []

    with internetdriver as driver:
        driver.get(URL)

        # Click add columns button
        driver.find_element(
            By.XPATH, '//span[contains(text(), "Add/Remove Columns")]').click()
        # click button to add freezing level to table
        driver.find_element(
            By.XPATH, '//span[contains(text(), "HGT_0C_DB")]').click()
        # Send escape key to exit add columns dialog box
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        soup = BeautifulSoup(driver.page_source, 'lxml')
        # select all the table rows
        for item in soup.select("table#example tbody tr"):
            # grab the text for each td tag
            data = [elem.text for elem in item.select('td')]
            # append the list of td text to the broader list, creating a list of lists
            list.append(data)

    df = pd.DataFrame(list, columns=["Datetime", "TMP", "DPT", "RH", "WS", "WD", "WG",
                      "APCP", "Cloud", "SLP", "HGT_0C_DB"])  # Create dataframe and name columns

    # Data cleanup and conversion
    df["Datetime"] = pd.to_datetime(df.Datetime)
    df.rename({"HGT_0C_DB": "Freezing Level"}, axis="columns",
              inplace=True)  # Renames Freezing level column
    converttonumeric = df.columns.drop('Datetime')
    df[converttonumeric] = df[converttonumeric].apply(
        pd.to_numeric, errors='coerce')

    html = df.to_html()
    # print(html)


    #### get components to form HTML page ####
   
    page = render_template('test.html', forecast_table=html)
    return page


if __name__ == "__main__":
    app.run(debug=True,
            threaded=False
            )

