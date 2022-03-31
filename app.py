import os
from cgitb import html
from flask import Flask, render_template
from bokeh.embed import components
from bokeh.plotting import figure
import pandas as pd
from matplotlib.font_manager import list_fonts
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.palettes import Spectral11
from bokeh.embed import file_html
from bokeh.plotting import figure, output_file, save

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
# ChromePATH = r"C:\Users\timtr\Documents\Coding\Dev_Tools\chromedriver.exe"   #The random r before the path converts it to a raw string
internetdriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# internetdriver = webdriver.Chrome(ChromePATH, chrome_options=chrome_options)

app = Flask(__name__)

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

    # Line Chart

    bokehdata = ColumnDataSource(df)
    p = figure(width=1000, height=400, x_axis_type='datetime')
    p.line(x='Datetime', y='RH', source=bokehdata,
           line_color="#f46d43", line_width=3)
    p.title.text = 'Temperature forecast'
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Temp. Celcius'

    hover = HoverTool()
    hover.tooltips = [
        ('Time', '@Datetime{%H:%M}'),
        ('Wind Speed km/h', '@WS'),
    ]

    hover.formatters = {
        # Bokeh formatter docs here: https://docs.bokeh.org/en/2.4.0/docs/reference/models/formatters.html#datetimetickformatter
        '@Datetime': 'datetime',
    }

    p.add_tools(hover)

    #### get components to form HTML page ####
    script, div = components(p)

    page = render_template('test.html', div=div, script=script)
    return page


if __name__ == "__main__":
    app.run(debug=True,
            threaded=False
            )
