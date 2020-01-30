import pandas as pd
from setups import setup9_3
from datetime import datetime
import indicators_builder as bd
import talib


def build(data, setup, signal_validation=False, verbose=False):
	full_periods = [2, 3, 9, 14, 21, 26, 32, 50, 66, 72, 100, 200]
	lil_periods = [200, 72, 50, 21, 14, 9, 3, 2]

	# PROCESS ENTRYS
	if setup == '9.3':
		data, ref_idx, signal_idx = setup9_3(data, 0.01, 0.01, verbose=False)

		if signal_validation and signal_idx <= 0:
			return data, ref_idx, signal_idx

	# CHOOSE CANDLE TO STUDY
	# data['TARGET_REG'] = data['SIGNAL']
	
	price_ind = ['open', 'high', 'low']
	volume_ind = []
	norm_ind = []

	# GET INDICATORS
	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('SMA')
	# SMAs
	for p in full_periods:
		ma_name = f'CLOSE_SMA_{p}'
		price_ind.append(ma_name)
		data = data.join(pd.Series(talib.SMA(data['close'], p), name=ma_name))

	# data = bd.averages(data, 'SMA', full_periods, 'close')

	if verbose:
		print(datetime.now())
		print('EMA')
	# EMAs
	for p in full_periods:
		ma_name = f'CLOSE_EMA_{p}'
		price_ind.append(ma_name)
		data = data.join(pd.Series(talib.EMA(data['close'], p), name=ma_name))
		
	# data = bd.averages(data, 'EMA', full_periods, 'close')

	if verbose:
		print(datetime.now())
		print('TEMA')
	# TEMAs
	for p in full_periods:
		ma_name = f'CLOSE_TEMA_{p}'
		price_ind.append(ma_name)
		data = data.join(pd.Series(talib.TEMA(data['close'], p), name=ma_name))
		
	# data = bd.averages(data, 'TEMA', full_periods, 'close')

	if verbose:
		print(datetime.now())
		print('WMA')
	# WMAs
	for p in full_periods:
		ma_name = f'CLOSE_WMA_{p}'
		price_ind.append(ma_name)
		data = data.join(pd.Series(talib.WMA(data['close'], p), name=ma_name))
		
	# data = bd.averages(data, 'WMA', full_periods, 'close')

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('VOLUME')
	# MAs of VOLUME
	for p in full_periods:
		ma_name = f'VOLUME_SMA_{p}'
		volume_ind.append(ma_name)
		data = data.join(pd.Series(talib.EMA(data['volume'], p), name=ma_name))

	for p in full_periods:
		ma_name = f'VOLUME_EMA_{p}'
		volume_ind.append(ma_name)
		data = data.join(pd.Series(talib.EMA(data['volume'], p), name=ma_name))

	# data = bd.averages(data, 'SMA', full_periods, 'volume')
	# data = bd.averages(data, 'EMA', full_periods, 'volume')

	didi_types = ['SMA', 'EMA']

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('OBV')
	data = data.join(pd.Series(talib.OBV(data['close'], data['volume']), name='OBV'))
	
	# data = bd.obv(data)

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

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('HILO')
	# HiLo
	for type in didi_types:
		for p in full_periods:
			hi_name = type + '_HI_' + str(p)
			lo_name = type + '_LO_' + str(p)
			price_ind.append(hi_name)
			price_ind.append(hi_name)
			data = data.join(pd.Series(getattr(talib, type)(data['high'], p), name=hi_name))
			data[hi_name] = data[hi_name].shift(1)
			data = data.join(pd.Series(getattr(talib, type)(data['low'], p), name=lo_name))
			data[lo_name] = data[lo_name].shift(1)
		
		# data = bd.hilo(data, type, full_periods)

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('STOCH')
	# STOCH
	stoch_p = lil_periods  # [21, 14, 9, 5, 3]
	for i in range(len(stoch_p)):
		for j in range(i + 1, len(stoch_p)):
			for typ in range(3):
				fastk_p = stoch_p[i]
				slow_p = stoch_p[j]
				stoch_name = f'STOCH_{fastk_p}F_{slow_p}L_TYPE{typ}_'
				slowk, slowd = talib.STOCH(data['high'], data['low'], data['close'], fastk_p, slow_p, typ, slow_p, typ)
				data = data.join(pd.Series(slowk, name=stoch_name + 'K'))
				data = data.join(pd.Series(slowd, name=stoch_name + 'D'))
				norm_ind.append(stoch_name + 'K')
				norm_ind.append(stoch_name + 'D')
			
			# data = bd.stoch(data, stoch_p[i], stoch_p[j])

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('MACD')
	# MACD
	signal_p = lil_periods  # [21, 14, 9, 5, 3]
	macd_p = [[200, 72],
			  [72, 50],
			  [50, 21],
			  [21, 14],
			  [14, 9],
			  [9, 3],
			  [3, 2]]
	for m in range(len(macd_p)):
		for s in range(m, len(signal_p)):
			slow, fast, signal = macd_p[m][0], macd_p[m][1], signal_p[s]
			
			macd_name = f'MACD_{fast}_{slow}_{signal}_'
			macd, macdsignal, macdhist = talib.MACD(data['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal)
			data = data.join(pd.Series(macd, name=macd_name + 'MACD'))
			data = data.join(pd.Series(macdsignal, name=macd_name + 'SIGNAL'))
			data = data.join(pd.Series(macdhist, name=macd_name + 'HIST'))

			# data = bd.macd(data, macd_p[m][0], macd_p[m][1], signal_p[s])

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('RSI')
	# RSI
	for p in full_periods:
		rsi_name = 'RSI_' + str(p)
		norm_ind.append(rsi_name)
		rsi = talib.RSI(data['close'], p)
		data = data.join(pd.Series(rsi, name=rsi_name))
		
	# data = bd.rsi(data, rsi_p)

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('CCI')
	# CCI
	for p in full_periods:
		cci_name = 'CCI_' + str(p)
		norm_ind.append(cci_name)
		cci = talib.CCI(data['high'], data['low'], data['close'], p)
		data = data.join(pd.Series(cci, name=cci_name))
		
	# data = bd.cci(data, cci_p)

	if verbose:
		print(datetime.now())
		print(len(list(data)))
		print('TRIX')
	# TRIX
	for p in lil_periods:
		trix_name = 'TRIX_' + str(p)
		norm_ind.append(trix_name)
		rsi = talib.TRIX(data['close'], p)
		data = data.join(pd.Series(rsi, name=trix_name))
		
	# data = bd.trix(data, trix_p)

	# print('APPLY RULES/NORMALIZATION')
	# for col in data.columns:
	# 	if col not in ["timestamp",
	# 				   "adjusted_close",
	# 				   "dividend_amount",
	# 				   "split_coefficient",
	# 				   "REF",
	# 				   "SIGNAL",
	# 				   'TARGET_REG']:
	#
	# 		# 1
	# 		new_name = col + '_DIFF'
	# 		diff = pd.Series((data[col][1:].reset_index(drop=True) / data[col][:-1].reset_index(drop=True) - 1),
	# 						 name=new_name)
	#
	# 		data = data.join(diff)
	# 		data[new_name] = data[new_name].shift(1)
	#
	# 		# 2 PRICE
	# 		if col in price_ind:
	# 			data[f'close/{col}'] = data['close'] / data[col] - 1
	#
	# 		# 2 VOL
	# 		if col in volume_ind:
	# 			data[f'volume/{col}'] = data['volume'] / data[col] - 1
	#
	# 		if col not in norm_ind and col not in ['open', 'high', 'low', 'close', 'volume']:
	# 			data = data.drop(columns=[col])

	# CANDLES
	str_candle = []
	hammer = []
	for i in range(len(data)):
		str_candle.append(
			1 if abs(data.iloc[i]['close'] - data.iloc[i]['open']) > 0.5 * (
					data.iloc[i]['high'] - data.iloc[i]['low']) else 0)
		hammer.append(1 if data.iloc[i]['close'] == data.iloc[i]['high'] else 0)

	data['STRONG_CANDLE'] = str_candle
	data['HIGH_EQ_CLOSE'] = hammer

	# MAKE TARGETS
	# if not signal_validation:
	# 	data = data.dropna(subset=['TARGET_REG'])
	# data['TARGET_BIN'] = data['TARGET_REG'].apply(lambda x: 1 if x > 0 else 0)
	# for i in range(2, 4):
	# 	data[f'TARGET_Q{i}'] = pd.qcut(data['TARGET_REG'], i, labels=False)
	#
	# data.drop(columns=["timestamp",
	# 				   "close",
	# 				   "open",
	# 				   "high",
	# 				   "low",
	# 				   "volume",
	# 				   "adjusted_close",
	# 				   "dividend_amount",
	# 				   "split_coefficient",
	# 				   "REF",
	# 				   "SIGNAL"], inplace=True)

	return data#, ref_idx, signal_idx

# TEST & SAVE...
# data.to_csv(f'output/{dire}_{filename}_level{level}.csv', index=False)
