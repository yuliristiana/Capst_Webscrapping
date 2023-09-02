from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('tbody')
row_table = table.find_all('tr')

row_length = len(row_table)

temp = [] #initiating a list 

for i in range(0, 129):
    
    #get period time
    period_time = table.find_all('a', attrs={'class':'w'})[i].text
    
    #period currency
    period_currency = table.find_all('span', attrs={'class':'w'})[i].text
    
    temp.append((period_time, period_currency))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('period_time','period_currency'))

#insert data wrangling here
df['period_currency'] = df['period_currency'].str.replace('$1 = Rp', '')
df['period_currency'] = df['period_currency'].str.replace(',', '')
df['period_time'] = df['period_time'].astype('datetime64[ns]')
df['period_currency'] = df['period_currency'].astype('float64')
df = df.set_index('period_time')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["period_currency"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)