from cgitb import html
import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, render_template
import time
import selenium
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
import json
import re
import os

app = Flask(__name__)

@app.route('/')
def load_driver():
	heroku=True
	# driver profile
	options = webdriver.chrome.options.Options()
	# options so that it runs on Heroku
	if not heroku:
		options.add_argument("--disable-extensions")
		# options.add_argument("--headless")
		# use Chrome to access web (will update chrome driver if needed)
		chromedriver = webdriver.Chrome(
			ChromeDriverManager().install(), chrome_options=options
		)
	else:
		options.add_argument("--disable-extensions")
		options.add_argument("--headless")
		options.add_argument("--disable-dev-shm-usage")
		options.add_argument("--no-sandbox")
		options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
		chromedriver = webdriver.Chrome(
			executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options
		)

	URL = "https://spotwx.com/products/grib_index.php?model=nam_awphys&lat=49.81637&lon=-123.33601&tz=America/Vancouver&display=table"
	list = []
	with chromedriver as driver:
		driver.get(URL)

		# Click add columns button
		driver.find_element(By.XPATH, '//span[contains(text(), "Add/Remove Columns")]').click()
		# click button to add freezing level to table
		driver.find_element(By.XPATH, '//span[contains(text(), "HGT_0C_DB")]').click()
		# Send escape key to exit add columns dialog box
		webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

		soup = BeautifulSoup(driver.page_source, 'lxml')
		# select all the table rows
		for item in soup.select("table#example tbody tr"):
			# grab the text for each td tag
			data = [elem.text for elem in item.select('td')]
			# append the list of td text to the broader list, creating a list of lists
			list.append(data)

			df = pd.DataFrame(list, columns=["Datetime", "TMP", "DPT", "RH", "WS", "WD", "WG", "APCP", "Cloud", "SLP", "HGT_0C_DB"])  # Create dataframe and name columns

			# Data cleanup and conversion
			# df.set_index("Datetime", inplace=True)
			# df["Datetime"] = pd.to_datetime(df.Datetime)
			# df.rename({"HGT_0C_DB": "Freezing Level"}, axis="columns",
			# inplace=True)  # Renames Freezing level column
			# converttonumeric = df.columns.drop('Datetime')
			# df[converttonumeric] = df[converttonumeric].apply(
			# pd.to_numeric, errors='coerce')
			# df.columns

			html = df.to_html()
	
	#### get components to form HTML page ####

	page = render_template('test.html', forecast_table=html)
	return page

if __name__ == "__main__":
		# start()
		app.run(debug=True,
		threaded=False
		)
		

