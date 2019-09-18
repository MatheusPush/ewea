import pandas as pd
from setups import setup9_3
from datetime import datetime
import indicators_builder as bd


def build(data, level, setup, signal_validation=False):

	if level == 1:
		full_periods = [3, 5, 7, 9, 11, 14, 16, 18, 21]
		lil_periods = [21, 14, 9, 5, 3]
	elif level == 2:
		full_periods = [21, 23, 26, 29, 32, 35, 40, 44, 50]
		lil_periods = [50, 32, 26, 21]
	elif level == 3:
		full_periods = [50, 60, 66, 72, 80, 90, 100]
		lil_periods = [100, 80, 72, 66, 50]
	elif level == 3.5:
		full_periods = [50, 66, 72, 80, 100, 120, 160, 200]
		lil_periods = [200, 100, 80, 72, 66, 50]
	elif level == 4:
		full_periods = [100, 120, 160, 200, 220, 300, 400, 440]
		lil_periods = [400, 200, 100]
	else:
		exit(1)

	# LOAD FILE
	# data = pd.read_csv(f'{dire}/{filename}.csv')

	# PROCESS ENTRYS
	if setup == '9.3':
		data, ref_idx, signal_idx = setup9_3(data, 0.1, 0.1)

		if signal_validation and signal_idx <= 0:
			return data, ref_idx, signal_idx


	# CHOOSE CANDLE TO STUDY
	data['TARGET_REG'] = data['SIGNAL']

	# GET INDICATORS
	# print(datetime.now())
	# print(len(list(data)))
	# print('SMA')
	# SMAs
	data = bd.averages(data, 'SMA', [3, 5, 7, 9, 11, 14, 16, 18, 21], 'close')

	# print(datetime.now())
	# print('EMA')
	# EMAs
	data = bd.averages(data, 'EMA', [3, 5, 7, 9, 11, 14, 16, 18, 21], 'close')

	# print(datetime.now())
	# print('TEMA')
	# TEMAs
	data = bd.averages(data, 'TEMA', [3, 5, 7, 9, 11, 14, 16, 18, 21], 'close')

	# print(datetime.now())
	# print('WMA')
	# WMAs
	data = bd.averages(data, 'WMA', [3, 5, 7, 9, 11, 14, 16, 18, 21], 'close')

	# print(datetime.now())
	# print(len(list(data)))
	# print('VOLUME')
	# MAs of VOLUME
	data = bd.averages(data, 'SMA', [3, 5, 7, 9, 11, 14, 16, 18, 21], 'volume')
	data = bd.averages(data, 'EMA', [3, 5, 7, 9, 11, 14, 16, 18, 21], 'volume')

	didi_types = ['SMA', 'EMA']
	# print(datetime.now())
	# print(len(list(data)))
	# print('OBV')
	# # SMAs
	# data = bd.obv(data)
	#
	# print(datetime.now())
	# print(len(list(data)))
	# print('DMI')
	# # DMI
	# dmi_list = [3, 9, 14, 21, 26]
	# for i in range(len(dmi_list)):
	# 	for j in range(i + 1, len(dmi_list)):
	# 		data = bd.dmi(data, dmi_list[i], dmi_list[j])
	#
	#
	# print(datetime.now())
	# print(len(list(data)))
	# print('DIDI')
	# # DIDI
	# didi_list1 = [2, 3]
	# didi_list2 = [6, 9]
	# didi_list3 = [14, 21, 26]
	#
	# for i in didi_list1:
	# 	for j in didi_list2:
	# 		for k in didi_list3:
	# 			for type in didi_types:
	# 				data = bd.didi(data, i, j, k, type)

	# print(datetime.now())
	# print(len(list(data)))
	# print('HILO')
	# HiLo
	for type in didi_types:
		data = bd.hilo(data, type, [3, 5, 7, 9, 11, 14, 16, 18, 21])

	# print(datetime.now())
	# print(len(list(data)))
	# print('STOCH')
	# STOCH
	stoch_p = [21, 14, 9, 5, 3]
	for i in range(len(stoch_p)):
		for j in range(i + 1, len(stoch_p)):
			data = bd.stoch(data, stoch_p[i], stoch_p[j])

	# print(datetime.now())
	# print(len(list(data)))
	# print('MACD')
	# MACD
	signal_p = [21, 14, 9, 5, 3]
	macd_p = [[21, 14],
			  [14, 9],
			  [9, 5]]
	for m in range(len(macd_p)):
		for s in range(m, len(signal_p)):
			data = bd.macd(data, macd_p[m][0], macd_p[m][1], signal_p[s])

	# print(datetime.now())
	# print(len(list(data)))
	# print('RSI')
	# RSI
	rsi_p = [3, 5, 7, 9, 11, 14, 16, 18, 21]
	data = bd.rsi(data, rsi_p)

	# print(datetime.now())
	# print(len(list(data)))
	# print('CCI')
	# CCI
	cci_p = [3, 5, 7, 9, 11, 14, 16, 18, 21]
	data = bd.cci(data, cci_p)

	# print(datetime.now())
	# print(len(list(data)))
	# print('TRIX')
	# TRIX
	trix_p = [21, 14, 9, 5, 3]
	data = bd.trix(data, trix_p)

	# CANDLES
	str_candle = []
	hammer = []
	for i in range(len(data)):
		str_candle.append(
			1 if abs(data.iloc[i]['close'] - data.iloc[i]['open']) > 0.5 * (
						data.iloc[i]['high'] - data.iloc[i]['low']) else 0)
		hammer.append(1 if data.iloc[i]['close'] == data.iloc[i]['high'] else 0)

	data['STR_CANDLE'] = str_candle
	data['HIGH_CLOSE'] = hammer

	# MAKE TARGETS
	if not signal_validation:
		data = data.dropna(subset=['TARGET_REG'])
	data['TARGET_BIN'] = data['TARGET_REG'].apply(lambda x: 1 if x > 0 else 0)
	# for i in range(2, 6):
	# 	data[f'TARGET_Q{i}'] = pd.qcut(data['TARGET_REG'], i, labels=False)

	data.drop(columns=["timestamp",
					   "close",
					   "open",
					   "high",
					   "low",
					   "volume",
					   "adjusted_close",
					   "dividend_amount",
					   "split_coefficient",
					   "REF",
					   "SIGNAL"], inplace=True)

	return data, ref_idx, signal_idx

	# TEST & SAVE...
	# data.to_csv(f'output/{dire}_{filename}_level{level}.csv', index=False)
