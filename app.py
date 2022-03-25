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
from bs4 import BeautifulSoup
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.palettes import Spectral11
from bokeh.embed import file_html
from bokeh.plotting import figure, output_file, save

app = Flask(__name__)

@app.route('/')
def test():
    ChromePATH = r"C:\Users\timtr\Documents\Coding\Dev_Tools\chromedriver.exe"   #The random r before the path converts it to a raw string
    URL = "https://spotwx.com/products/grib_index.php?model=nam_awphys&lat=49.81637&lon=-123.33601&tz=America/Vancouver&display=table"
    list=[]

    with webdriver.Chrome(ChromePATH) as driver:
        driver.get(URL)

        driver.find_element(By.XPATH, '//span[contains(text(), "Add/Remove Columns")]').click() #Click add columns button
        driver.find_element(By.XPATH, '//span[contains(text(), "HGT_0C_DB")]').click() #click button to add freezing level to table
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform() #Send escape key to exit add columns dialog box

        soup = BeautifulSoup(driver.page_source, 'lxml')
        for item in soup.select("table#example tbody tr"): #select all the table rows
            data = [elem.text for elem in item.select('td')] #grab the text for each td tag
            list.append(data) #append the list of td text to the broader list, creating a list of lists

    df = pd.DataFrame(list, columns=["Datetime", "TMP", "DPT", "RH", "WS", "WD", "WG", "APCP", "Cloud", "SLP", "HGT_0C_DB"]) #Create dataframe and name columns

    # Data cleanup and conversion
    df["Datetime"] = pd.to_datetime(df.Datetime)
    df.rename({"HGT_0C_DB": "Freezing Level"}, axis="columns", inplace=True)   #Renames Freezing level column
    converttonumeric = df.columns.drop('Datetime')
    df[converttonumeric] = df[converttonumeric].apply(pd.to_numeric, errors='coerce')


    # Line Chart
    output_file(filename="spotwx.html", title="SpotWX data scrape")

    bokehdata = ColumnDataSource(df)
    p = figure(width=1000, height=400, x_axis_type='datetime')
    p.line(x='Datetime', y='RH', source=bokehdata, line_color="#f46d43", line_width=3)
    p.title.text = 'Temperature forecast'
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Temp. Celcius'

    hover = HoverTool()
    hover.tooltips=[
        ('Time', '@Datetime{%H:%M}'),
        ('Wind Speed km/h', '@WS'),
        ]

    hover.formatters={
        '@Datetime': 'datetime', # Bokeh formatter docs here: https://docs.bokeh.org/en/2.4.0/docs/reference/models/formatters.html#datetimetickformatter
        }

    p.add_tools(hover)

    # show(p)
    # save(p)


    #### get components ####
    script, div = components(p)

    page = render_template('test.html', div=div, script=script)
    return page


if __name__ == "__main__":
    app.run(debug=True,
            threaded=False
            )