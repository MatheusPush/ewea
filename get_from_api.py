import requests
import pandas as pd
from io import StringIO
from v2.dataset_builder import build

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
		  'NATU3'
		  ]

all_stocks = []

for stock in papers:
	try:
		print(f'STOCK: {stock}')
		while True:
			req = requests.get('https://www.alphavantage.co/' + \
							   f'query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock}.SA' + \
							   '&outputsize=full&apikey=JX8UCTKQOPU5WOZZ&datatype=csv')

			if req.status_code == 200:
				stock_df = pd.read_csv(StringIO(req.text))
				break

		stock_df = stock_df.round(2)
		stock_df['dividend_amount'] = stock_df['close'] - stock_df['adjusted_close']
		stock_df['adjusted_open'] = stock_df['open'] - stock_df['dividend_amount']
		stock_df['adjusted_high'] = stock_df['high'] - stock_df['dividend_amount']
		stock_df['adjusted_low'] = stock_df['open'] - stock_df['dividend_amount']
		stock_df = stock_df.sort_values(['timestamp'])
		stock_df['timestamp'] = pd.to_datetime(stock_df['timestamp'], format='%Y-%m-%d')
		stock_df = stock_df[stock_df['timestamp'] > '2005-01-01'].reset_index(drop=True)

		stock_df = build(stock_df, '', verbose=True)

		stock_df['STOCK'] = [stock] * len(stock_df)
		stock_df = stock_df.round(3)

		all_stocks.append(stock_df)
	except Exception as e:
		print(f'DEU BOSTA IRMAO: {stock}\n\n{e}')

full_df = pd.concat(all_stocks)

# todo FILL NA 0

print('SAVING FILE...')
print(full_df.shape)

full_df.to_csv(f'v2/full_dataset.csv', index=False)
