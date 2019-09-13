import requests
import pandas as pd
from io import StringIO
from dataset_builder import build

papers = ['PETR4',
		  'VALE3',
		  'BBDC4',
		  'BBAS3',
		  'B3SA3',
		  'MGLU3',
		  'ABEV3',
		  'BPAC11',
		  'JBSS3',
		  'ITSA4',
		  'VVAR3',
		  'BRFS3',
		  'GGBR4',
		  'ELET3',
		  'RENT3',
		  'LREN3',
		  'MRVE3',
		  'CYRE3',
		  'BTOW3',
		  'CMIG4',
		  'CSNA3',
		  'GOLL4',
		  'SBSP3',
		  'SULA11',
		  'CIEL3',
		  'QUAL3',
		  'EQTL3',
		  'USIM5',
		  'NATU3']

all_stocks = []

for stock in papers:
	try:
		print(f'STOCK: {stock}')

		req = requests.get('https://www.alphavantage.co/' + \
						   f'query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock}.SA' + \
						   '&outputsize=full&apikey=JX8UCTKQOPU5WOZZ&datatype=csv')
		stock_df = pd.read_csv(StringIO(req.text))

		stock_df = stock_df.sort_values(['timestamp'])
		stock_df['timestamp'] = pd.to_datetime(stock_df['timestamp'], format='%Y-%m-%d')
		stock_df = stock_df[stock_df['timestamp'] > '2010-01-01'].reset_index(drop=True)

		stock_df = build(stock_df, 1, '9.3')

		all_stocks.append(stock_df)
	except Exception as e:
		print(f'DEU BOSTA IRMAO: {stock}\n\n{e}')

full_df = pd.concat(all_stocks)

print('SAVING FILE...')

full_df.to_csv(f'output/all_stocks_dataset.csv', index=False)
