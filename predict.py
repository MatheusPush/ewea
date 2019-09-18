import requests
import pandas as pd
from io import StringIO
import joblib as jbl
from dataset_builder import build
import numpy as np

model = jbl.load('log_reg-elasticnet-C02_-l1r04.jbl')

papers = ['PETR4',
		  'ITSA4',
		  'ITUB4',
		  'VALE3',
		  'BBDC4',
		  'BBAS3',
		  'B3SA3',
		  'MGLU3',
		  'ABEV3',
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
		  'NATU3',
		  'AMAR3',
		  'BBSE3',
		  'FLRY3',
		  'BRAP4',
		  'CCRO3',
		  'LAME4',
		  'CVCB3',
		  'RAIL3',
		  'UGPA3',
		  'BIDI4',
		  'SQIA3',
		  'KROT3',
		  'AZUL4',
		  'IRBR3',
		  'PCAR4',
		  'BOVA11',
		  'BPAC11',
		  'OIBR3',
		  'BRDT3',
		  'BRML3',
		  'GNDI3',
		  'MRVE3',
		  'BRKM5',
		  'MULT3']

for stock in papers:
	while True:
		req = requests.get('https://www.alphavantage.co/' + \
						   f'query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock}.SA' + \
						   '&outputsize=compact&apikey=JX8UCTKQOPU5WOZZ&datatype=csv')
		stock_df = pd.read_csv(StringIO(req.text))

		if 'timestamp' in stock_df.columns:
			break

	stock_df = stock_df[1:]

	stock_df = stock_df.sort_values(['timestamp']).reset_index(drop=True)
	stock_df['timestamp'] = pd.to_datetime(stock_df['timestamp'], format='%Y-%m-%d')

	stock_df, ref_idx, signal_idx = build(stock_df, 1, '9.3', signal_validation=True)

	if signal_idx == stock_df.index.max():
		stock_df.drop(['TARGET_REG', 'TARGET_BIN'], axis=1, inplace=True)
		X = np.asarray([stock_df.loc[signal_idx].values])
		y_pred_proba = model.predict_proba(X)
		prob = y_pred_proba[0, 1]
		print(f'\n\n # SINAL DE COMPRA EM {stock} COM {format(prob * 100, ".2f")}% DE CONFIANÇA!\n\n')
