import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import pandas as pd

GECKODRIVER_PATH = r"C:\Users\timtr\Documents\Coding\Dev_Tools\geckodriver.exe"
FIREFOX_BIN = r"C:\Program Files\Mozilla Firefox\firefox.exe"

def load_driver():
	
	option = Options()
	# enable trace level for debugging 
	option.log.level = "trace"
	# options.add_argument("-remote-debugging-port=9224")
	# options.add_argument("-headless")
	option.add_argument("-disable-gpu")
	option.add_argument("-no-sandbox") 
	option.binary_location=FIREFOX_BIN
	driverService = Service(GECKODRIVER_PATH)
	firefox_driver = webdriver.Firefox(service=driverService, options=option)

	return firefox_driver

def  start():
	driver = load_driver()
	URL = "https://spotwx.com/products/grib_index.php?model=nam_awphys&lat=49.81637&lon=-123.33601&tz=America/Vancouver&display=table"
	list = []
	with driver as driver:
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

	df = pd.DataFrame(list, columns=["Datetime", "TMP", "DPT", "RH", "WS", "WD", "WG", "APCP", "Cloud", "SLP", "HGT_0C_DB"])  # Create dataframe and name columns

	# Data cleanup and conversion
	df["Datetime"] = pd.to_datetime(df.Datetime)
	df.rename({"HGT_0C_DB": "Freezing Level"}, axis="columns",
	inplace=True)  # Renames Freezing level column
	converttonumeric = df.columns.drop('Datetime')
	df[converttonumeric] = df[converttonumeric].apply(
	pd.to_numeric, errors='coerce')

	html = df.to_html()
	print(html)

if  __name__ == "__main__":
	start()