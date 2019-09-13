import pandas as pd
import numpy as np
import talib
import plotly.plotly as py
import plotly.graph_objs as go
from datetime import datetime


def do_uptrend(source: pd.DataFrame, name):
	uptrend = pd.Series((source[name][1:].reset_index(drop=True) >
						 source[name][:-1].reset_index(drop=True)).astype('int'), name=name + "_UP")

	source = source.join(uptrend)

	source[name + "_UP"] = source[name + "_UP"].shift(1)

	return source


def do_over(source, name_up, name_down):
	over = pd.Series((source[name_up] > source[name_down]).astype('int'), name=name_up + "_OVER_" + name_down)

	source = source.join(over)

	# source = do_cross(source, name_up + "_OVER_" + name_down)

	return source


def do_cross(source, name):
	fst = source[name][:-1].astype('bool').reset_index(drop=True).values
	sec = source[name][1:].astype('bool').reset_index(drop=True).values
	cross_up = []
	cross_down = []

	for i in range(len(fst)):
		cross_up.append(not fst[i] and sec[i])
		cross_down.append(fst[i] and not sec[i])

	cross_up = pd.Series(cross_up, name=name + "_CROSSUP")
	cross_down = pd.Series(cross_down, name=name + "_CROSSDOWN")

	source = source.join(cross_up)
	source = source.join(cross_down)

	source[name + "_CROSSUP"] = source[name + "_CROSSUP"].shift(1)
	source[name + "_CROSSDOWN"] = source[name + "_CROSSDOWN"].shift(1)

	return source


def do_above(source, name, level):
	over = pd.Series((source[name] > level).astype('int'), name=name + "_ABOVE_" + str(level))

	source = source.join(over)

	# source = do_cross(source, name + "_ABOVE_" + str(level))

	return source


def averages(source, type, periods, basis):
	price = source[basis]

	for p in periods:
		sma_name = basis + '_' + type + '_' + str(p)
		source = source.join(pd.Series(getattr(talib, type)(price, p), name=sma_name))

	# Trends
	for p in periods:
		sma_name = basis + '_' + type + '_' + str(p)
		source = do_uptrend(source, sma_name)

	# Over
	periods = [basis] + periods
	for i in range(len(periods)):
		for j in range(i + 1, len(periods)):
			sma_name1 = basis + '_' + type + '_' + str(periods[i]) if periods[i] != basis else basis
			sma_name2 = basis + '_' + type + '_' + str(periods[j])
			source = do_over(source, sma_name1, sma_name2)

	for p in periods:
		if p != basis:
			sma_name = basis + '_' + type + '_' + str(p)
			source = source.drop(columns=[sma_name])

	return source


def vwap(source):
	return (source['volume'] * (source['high'] + source['low']) / 2).cumsum() / source['volume'].cumsum()


def hilo(source, type, periods):
	hi = source['high']
	lo = source['low']

	for p in periods:
		hi_name = type + '_HI_' + str(p)
		lo_name = type + '_LO_' + str(p)
		source = source.join(pd.Series(getattr(talib, type)(hi, p), name=hi_name))
		source[hi_name] = source[hi_name].shift(1)
		source = source.join(pd.Series(getattr(talib, type)(lo, p), name=lo_name))
		source[lo_name] = source[lo_name].shift(1)

	# Trends
	for p in periods:
		hi_name = type + '_HI_' + str(p)
		lo_name = type + '_LO_' + str(p)
		source = do_uptrend(source, hi_name)
		source = do_uptrend(source, lo_name)

	# Over
	for p in periods:
		hi_name = type + '_HI_' + str(p)
		lo_name = type + '_LO_' + str(p)
		source = do_over(source, 'close', hi_name)
		source = do_over(source, 'close', lo_name)

	# Drop
	for p in periods:
		hi_name = type + '_HI_' + str(p)
		lo_name = type + '_LO_' + str(p)
		source = source.drop(columns=[hi_name, lo_name])

	return source


def didi(source, short, mid, long, type):
	price = source['close']

	short_sma = getattr(talib, type)(price, short)
	mid_sma = getattr(talib, type)(price, mid)
	long_sma = getattr(talib, type)(price, long)
	didi_short = short_sma - mid_sma
	didi_long = long_sma - mid_sma

	long_name = "DIDI_LONG_" + str(short) + "/" + str(mid) + "/" + str(long) + "_TYPE" + type
	short_name = "DIDI_SHORT_" + str(short) + "/" + str(mid) + "/" + str(long) + "_TYPE" + type

	source = source.join(pd.Series(didi_short, name=short_name))
	source = source.join(pd.Series(didi_long, name=long_name))

	# Trends
	source = do_uptrend(source, short_name)
	source = do_uptrend(source, long_name)

	# Over
	source = do_over(source, short_name, long_name)

	# Above Mid (0)
	source = do_above(source, short_name, 0)
	source = do_above(source, long_name, 0)

	source = source.drop(columns=[short_name, long_name])

	return source

def super_didi(source, short, mid, long, longlong, type):
	price = source['close']

	short_sma = getattr(talib, type)(price, short)
	mid_sma = getattr(talib, type)(price, mid)
	long_sma = getattr(talib, type)(price, long)
	longlong_sma = getattr(talib, type)(price, longlong)

	didi_shortshort = price - mid_sma
	didi_short = short_sma - mid_sma
	didi_long = long_sma - mid_sma
	didi_longlong = longlong_sma - mid_sma

	longlong_name = "SUPERDIDI_LONGLONG_" + str(longlong) + "_TYPE" + type
	long_name = "SUPERDIDI_LONG_" + str(long) + "_TYPE" + type
	short_name = "SUPERDIDI_SHORT_" + str(short) + "_TYPE" + type
	shortshort_name = "SUPERDIDI_SHORTSHORT_CLOSE_TYPE" + type

	source = source.join(pd.Series(didi_shortshort, name=shortshort_name))
	source = source.join(pd.Series(didi_short, name=short_name))
	source = source.join(pd.Series(didi_long, name=long_name))
	source = source.join(pd.Series(didi_longlong, name=longlong_name))

	# Trends
	source = do_uptrend(source, shortshort_name)
	source = do_uptrend(source, short_name)
	source = do_uptrend(source, long_name)
	source = do_uptrend(source, longlong_name)

	# Over
	source = do_over(source, shortshort_name, short_name)
	source = do_over(source, shortshort_name, long_name)
	source = do_over(source, shortshort_name, longlong_name)

	source = do_over(source, short_name, long_name)
	source = do_over(source, short_name, longlong_name)

	source = do_over(source, long_name, longlong_name)

	# Above Mid (0)
	source = do_above(source, shortshort_name, 0)
	source = do_above(source, short_name, 0)
	source = do_above(source, long_name, 0)
	source = do_above(source, longlong_name, 0)

	source = source.drop(columns=[shortshort_name, short_name, long_name, longlong_name])

	return source


# ADXR?			> https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/momentum_indicators.md
def dmi(source, dmi_period, dmi_smooth):
	minus_name = "MINUS_DI_" + str(dmi_period) + "_" + str(dmi_smooth)
	plus_name = "PLUS_DI_" + str(dmi_period) + "_" + str(dmi_smooth)
	adx_name = "ADX_" + str(dmi_period) + "_" + str(dmi_smooth)

	source = source.join(
		pd.Series(talib.MINUS_DI(source['high'], source['low'], source['close'], timeperiod=dmi_period),
				  name=minus_name))
	source = source.join(pd.Series(talib.PLUS_DI(source['high'], source['low'], source['close'], timeperiod=dmi_period),
								   name=plus_name))
	source = source.join(pd.Series(talib.ADX(source['high'], source['low'], source['close'], timeperiod=dmi_smooth),
								   name=adx_name))

	# Trends
	source = do_uptrend(source, adx_name)
	source = do_uptrend(source, plus_name)
	source = do_uptrend(source, minus_name)

	# Overs
	source = do_over(source, adx_name, plus_name)
	source = do_over(source, adx_name, minus_name)
	source = do_over(source, plus_name, minus_name)

	# Aboves
	for level in range(10, 51, 10):
		source = do_above(source, adx_name, level)
		source = do_above(source, plus_name, level)
		source = do_above(source, minus_name, level)

	source = source.drop(columns=[adx_name, plus_name, minus_name])

	return source


def bbands(source, periods, devs):
	price = source['close']

	for i in range(3):
		for p in periods:
			for d in devs:
				bbands_name = '_TYPE' + str(i) + '_' + str(p) + 'P_' + str(d) + 'DEV'
				upperband, middleband, lowerband = talib.BBANDS(price, p, d, d, matype=i)
				source = source.join(pd.Series(upperband, name='UPPERBAND' + bbands_name))
				source = source.join(pd.Series(lowerband, name='LOWERBAND' + bbands_name))
				source = source.join(pd.Series(upperband - lowerband, name='BBW' + bbands_name))

	# Trends
	for i in range(3):
		for p in periods:
			for d in devs:
				bbands_name = '_TYPE' + str(i) + '_' + str(p) + 'P_' + str(d) + 'DEV'
				source = do_uptrend(source, 'UPPERBAND' + bbands_name)
				source = do_uptrend(source, 'LOWERBAND' + bbands_name)
				source = do_uptrend(source, 'BBW' + bbands_name)

	# Over
	for i in range(3):
		for p in periods:
			for d in devs:
				bbands_name = '_TYPE' + str(i) + '_' + str(p) + 'P_' + str(d) + 'DEV'
				source = do_over(source, 'close', 'UPPERBAND' + bbands_name)
				source = do_over(source, 'close', 'LOWERBAND' + bbands_name)

	# Above
	for i in range(3):
		for p in periods:
			for d in devs:
				for level in range(1, 11):
					bbands_name = '_TYPE' + str(i) + '_' + str(p) + 'P_' + str(d) + 'DEV'
					source = do_above(source, 'BBW' + bbands_name, level/10)

	# Drop
	for i in range(3):
		for p in periods:
			for d in devs:
				bbands_name = '_TYPE' + str(i) + '_' + str(p) + 'P_' + str(d) + 'DEV'
				source = source.drop(
					columns=['UPPERBAND' + bbands_name, 'LOWERBAND' + bbands_name, 'BBW' + bbands_name])

	return source


def stoch(source, fastk_p, slow_p):
	high = source['high']
	low = source['low']
	close = source['close']

	for type in range(3):
		stoch_name = 'STOCH_' + str(fastk_p) + 'FAST_' + str(slow_p) + 'SLOW_TYPE' + str(type) + '_'
		slowk, slowd = talib.STOCH(high, low, close, fastk_p, slow_p, type, slow_p, type)
		source = source.join(pd.Series(slowk, name=stoch_name + '%K'))
		source = source.join(pd.Series(slowd, name=stoch_name + '%D'))

	# Trends
	for type in range(3):
		stoch_name = 'STOCH_' + str(fastk_p) + 'FAST_' + str(slow_p) + 'SLOW_TYPE' + str(type) + '_'
		source = do_uptrend(source, stoch_name + '%K')
		source = do_uptrend(source, stoch_name + '%D')

	# Over
	for type in range(3):
		stoch_name = 'STOCH_' + str(fastk_p) + 'FAST_' + str(slow_p) + 'SLOW_TYPE' + str(type) + '_'
		source = do_over(source, stoch_name + '%K', stoch_name + '%D')

	# Above
	for type in range(3):
		for level in range(25, 100, 25):
			stoch_name = 'STOCH_' + str(fastk_p) + 'FAST_' + str(slow_p) + 'SLOW_TYPE' + str(type) + '_'
			source = do_above(source, stoch_name + '%K', level)
			source = do_above(source, stoch_name + '%D', level)

	# Drop
	for type in range(3):
		stoch_name = 'STOCH_' + str(fastk_p) + 'FAST_' + str(slow_p) + 'SLOW_TYPE' + str(type) + '_'
		source = source.drop(columns=[stoch_name + '%K', stoch_name + '%D'])

	return source


def rsi(source, periods):
	price = source['close']

	for p in periods:
		rsi_name = 'RSI_' + str(p)
		rsi = talib.RSI(price, p)
		source = source.join(pd.Series(rsi, name=rsi_name))

	# Trends
	for p in periods:
		rsi_name = 'RSI_' + str(p)
		source = do_uptrend(source, rsi_name)

	# Over
	for i in range(len(periods)):
		for j in range(i + 1, len(periods)):
			rsi_name1 = 'RSI_' + str(periods[i])
			rsi_name2 = 'RSI_' + str(periods[j])
			source = do_over(source, rsi_name1, rsi_name2)

	# Above
	for p in periods:
		for level in range(25, 100, 25):
			rsi_name = 'RSI_' + str(p)
			source = do_above(source, rsi_name, level)

	# Drop
	for p in periods:
		rsi_name = 'RSI_' + str(p)
		source = source.drop(columns=[rsi_name])

	return source


def trix(source, periods):
	price = source['close']

	for p in periods:
		trix_name = 'TRIX_' + str(p)
		rsi = talib.TRIX(price, p)
		source = source.join(pd.Series(rsi, name=trix_name))

	# Trends
	for p in periods:
		trix_name = 'TRIX_' + str(p)
		source = do_uptrend(source, trix_name)

	# Over
	for i in range(len(periods)):
		for j in range(i + 1, len(periods)):
			trix_name1 = 'TRIX_' + str(periods[i])
			trix_name2 = 'TRIX_' + str(periods[j])
			source = do_over(source, trix_name1, trix_name2)

	# Above
	for p in periods:
		trix_name = 'TRIX_' + str(p)
		source = do_above(source, trix_name, 0)

	# Drop
	for p in periods:
		trix_name = 'TRIX_' + str(p)
		source = source.drop(columns=[trix_name])

	return source


def cci(source, periods):

	for p in periods:
		cci_name = 'CCI_' + str(p)
		cci = talib.CCI(source['high'], source['low'], source['close'], p)
		source = source.join(pd.Series(cci, name=cci_name))

	# Trends
	for p in periods:
		cci_name = 'CCI_' + str(p)
		source = do_uptrend(source, cci_name)

	# Over
	for i in range(len(periods)):
		for j in range(i + 1, len(periods)):
			cci_name1 = 'CCI_' + str(periods[i])
			cci_name2 = 'CCI_' + str(periods[j])
			source = do_over(source, cci_name1, cci_name2)

	# Above
	for p in periods:
		for level in [-200, -150, -100, -50, 0, 50, 100, 150, 200]:
			cci_name = 'CCI_' + str(p)
			source = do_above(source, cci_name, level)

	# Drop
	for p in periods:
		cci_name = 'CCI_' + str(p)
		source = source.drop(columns=[cci_name])

	return source


def macd(source, slow, fast, signal):
	high = source['high']
	low = source['low']
	close = source['close']

	macd_name = 'MACD_' + str(fast) + '_' + str(slow) + '_' + str(signal) + '_'
	macd, macdsignal, macdhist = talib.MACD(close, fastperiod=fast, slowperiod=slow, signalperiod=signal)
	source = source.join(pd.Series(macd, name=macd_name + 'MACD'))
	source = source.join(pd.Series(macdsignal, name=macd_name + 'SIGNAL'))
	source = source.join(pd.Series(macdhist, name=macd_name + 'HIST'))

	# Trends
	source = do_uptrend(source, macd_name + 'MACD')
	source = do_uptrend(source, macd_name + 'SIGNAL')
	source = do_uptrend(source, macd_name + 'HIST')

	# Above
	source = do_above(source, macd_name + 'MACD', 0)
	source = do_above(source, macd_name + 'SIGNAL', 0)
	source = do_above(source, macd_name + 'HIST', 0)

	# Drop
	source = source.drop(columns=[macd_name + 'MACD', macd_name + 'SIGNAL', macd_name + 'HIST'])

	return source


def obv(source):

	obv_ = talib.OBV(source['close'], source['volume'])

	source = source.join(pd.Series(obv_, name='OBV'))

	source = do_uptrend(source, 'OBV')

	source = averages(source, 'SMA', [3, 9, 14, 21, 50, 100, 200, 400], 'OBV')

	source = source.drop(columns='OBV')

	return source


def candles(source):
	open = source['open']
	high = source['high']
	low = source['low']
	close = source['close']

	source = source.join(pd.Series(talib.CDL2CROWS(open, high, low, close), name='CDL2CROWS'))
	source = source.join(pd.Series(talib.CDL3BLACKCROWS(open, high, low, close), name='CDL3BLACKCROWS'))
	source = source.join(pd.Series(talib.CDL3INSIDE(open, high, low, close), name='CDL3INSIDE'))
	source = source.join(pd.Series(talib.CDL3OUTSIDE(open, high, low, close), name='CDL3OUTSIDE'))
	source = source.join(pd.Series(talib.CDL3STARSINSOUTH(open, high, low, close), name='CDL3STARSINSOUTH'))
	source = source.join(pd.Series(talib.CDL3WHITESOLDIERS(open, high, low, close), name='CDL3WHITESOLDIERS'))
	source = source.join(pd.Series(talib.CDLABANDONEDBABY(open, high, low, close), name='CDLABANDONEDBABY'))
	source = source.join(pd.Series(talib.CDLADVANCEBLOCK(open, high, low, close), name='CDLADVANCEBLOCK'))
	source = source.join(pd.Series(talib.CDLBELTHOLD(open, high, low, close), name='CDLBELTHOLD'))
	source = source.join(pd.Series(talib.CDLBREAKAWAY(open, high, low, close), name='CDLBREAKAWAY'))
	source = source.join(pd.Series(talib.CDLCLOSINGMARUBOZU(open, high, low, close), name='CDLCLOSINGMARUBOZU'))
	source = source.join(pd.Series(talib.CDLCONCEALBABYSWALL(open, high, low, close), name='CDLCONCEALBABYSWALL'))
	source = source.join(pd.Series(talib.CDLCOUNTERATTACK(open, high, low, close), name='CDLCOUNTERATTACK'))
	source = source.join(pd.Series(talib.CDLDARKCLOUDCOVER(open, high, low, close), name='CDLDARKCLOUDCOVER'))
	source = source.join(pd.Series(talib.CDLDOJI(open, high, low, close), name='CDLDOJI'))
	source = source.join(pd.Series(talib.CDLDOJISTAR(open, high, low, close), name='CDLDOJISTAR'))
	source = source.join(pd.Series(talib.CDLDRAGONFLYDOJI(open, high, low, close), name='CDLDRAGONFLYDOJI'))
	source = source.join(pd.Series(talib.CDLENGULFING(open, high, low, close), name='CDLENGULFING'))
	source = source.join(pd.Series(talib.CDLEVENINGDOJISTAR(open, high, low, close), name='CDLEVENINGDOJISTAR'))
	source = source.join(pd.Series(talib.CDLEVENINGSTAR(open, high, low, close), name='CDLEVENINGSTAR'))
	source = source.join(pd.Series(talib.CDLGAPSIDESIDEWHITE(open, high, low, close), name='CDLGAPSIDESIDEWHITE'))
	source = source.join(pd.Series(talib.CDLGRAVESTONEDOJI(open, high, low, close), name='CDLGRAVESTONEDOJI'))
	source = source.join(pd.Series(talib.CDLHAMMER(open, high, low, close), name='CDLHAMMER'))
	source = source.join(pd.Series(talib.CDLHANGINGMAN(open, high, low, close), name='CDLHANGINGMAN'))
	source = source.join(pd.Series(talib.CDLHARAMI(open, high, low, close), name='CDLHARAMI'))
	source = source.join(pd.Series(talib.CDLHARAMICROSS(open, high, low, close), name='CDLHARAMICROSS'))
	source = source.join(pd.Series(talib.CDLHIGHWAVE(open, high, low, close), name='CDLHIGHWAVE'))
	source = source.join(pd.Series(talib.CDLHIKKAKE(open, high, low, close), name='CDLHIKKAKE'))
	source = source.join(pd.Series(talib.CDLHIKKAKEMOD(open, high, low, close), name='CDLHIKKAKEMOD'))
	source = source.join(pd.Series(talib.CDLHOMINGPIGEON(open, high, low, close), name='CDLHOMINGPIGEON'))
	source = source.join(pd.Series(talib.CDLIDENTICAL3CROWS(open, high, low, close), name='CDLIDENTICAL3CROWS'))
	source = source.join(pd.Series(talib.CDLINNECK(open, high, low, close), name='CDLINNECK'))
	source = source.join(pd.Series(talib.CDLINVERTEDHAMMER(open, high, low, close), name='CDLINVERTEDHAMMER'))
	source = source.join(pd.Series(talib.CDLKICKING(open, high, low, close), name='CDLKICKING'))
	source = source.join(pd.Series(talib.CDLKICKINGBYLENGTH(open, high, low, close), name='CDLKICKINGBYLENGTH'))
	source = source.join(pd.Series(talib.CDLLADDERBOTTOM(open, high, low, close), name='CDLLADDERBOTTOM'))
	source = source.join(pd.Series(talib.CDLLONGLEGGEDDOJI(open, high, low, close), name='CDLLONGLEGGEDDOJI'))
	source = source.join(pd.Series(talib.CDLLONGLINE(open, high, low, close), name='CDLLONGLINE'))
	source = source.join(pd.Series(talib.CDLMARUBOZU(open, high, low, close), name='CDLMARUBOZU'))
	source = source.join(pd.Series(talib.CDLMATCHINGLOW(open, high, low, close), name='CDLMATCHINGLOW'))
	source = source.join(pd.Series(talib.CDLMATHOLD(open, high, low, close), name='CDLMATHOLD'))
	source = source.join(pd.Series(talib.CDLMORNINGDOJISTAR(open, high, low, close), name='CDLMORNINGDOJISTAR'))
	source = source.join(pd.Series(talib.CDLMORNINGSTAR(open, high, low, close), name='CDLMORNINGSTAR'))
	source = source.join(pd.Series(talib.CDLONNECK(open, high, low, close), name='CDLONNECK'))
	source = source.join(pd.Series(talib.CDLPIERCING(open, high, low, close), name='CDLPIERCING'))
	source = source.join(pd.Series(talib.CDLRICKSHAWMAN(open, high, low, close), name='CDLRICKSHAWMAN'))
	source = source.join(pd.Series(talib.CDLRISEFALL3METHODS(open, high, low, close), name='CDLRISEFALL3METHODS'))
	source = source.join(pd.Series(talib.CDLSEPARATINGLINES(open, high, low, close), name='CDLSEPARATINGLINES'))
	source = source.join(pd.Series(talib.CDLSHOOTINGSTAR(open, high, low, close), name='CDLSHOOTINGSTAR'))
	source = source.join(pd.Series(talib.CDLSHORTLINE(open, high, low, close), name='CDLSHORTLINE'))
	source = source.join(pd.Series(talib.CDLSPINNINGTOP(open, high, low, close), name='CDLSPINNINGTOP'))
	source = source.join(pd.Series(talib.CDLSTALLEDPATTERN(open, high, low, close), name='CDLSTALLEDPATTERN'))
	source = source.join(pd.Series(talib.CDLSTICKSANDWICH(open, high, low, close), name='CDLSTICKSANDWICH'))
	source = source.join(pd.Series(talib.CDLTAKURI(open, high, low, close), name='CDLTAKURI'))
	source = source.join(pd.Series(talib.CDLTASUKIGAP(open, high, low, close), name='CDLTASUKIGAP'))
	source = source.join(pd.Series(talib.CDLTHRUSTING(open, high, low, close), name='CDLTHRUSTING'))
	source = source.join(pd.Series(talib.CDLTRISTAR(open, high, low, close), name='CDLTRISTAR'))
	source = source.join(pd.Series(talib.CDLUNIQUE3RIVER(open, high, low, close), name='CDLUNIQUE3RIVER'))
	source = source.join(pd.Series(talib.CDLUPSIDEGAP2CROWS(open, high, low, close), name='CDLUPSIDEGAP2CROWS'))
	source = source.join(pd.Series(talib.CDLXSIDEGAP3METHODS(open, high, low, close), name='CDLXSIDEGAP3METHODS'))

	return source


def classification(source, size):
	size2 = size - 1
	top = [None] * size2
	bottom = [None] * size2

	for i in range(size2, len(source) - size2):
		# Top Class
		is_top, is_bottom = classify(source.iloc[i - size2:i + size].reset_index(), size2)
		top.append(is_top)
		bottom.append(is_bottom)

	top += [None] * size2
	bottom += [None] * size2

	source = source.join(pd.Series(top, name='IS_TOP'))
	source = source.join(pd.Series(bottom, name='IS_BOTTOM'))

	return source


def classify(array: pd.DataFrame, size):
	top_idx = array['high'].idxmax()
	bottom_idx = array['low'].idxmin()

	return int(top_idx == size), int(bottom_idx == size)


def str_candles(source):
	str_candle = []
	for i in range(len(source)):
		str_candle.append(
			1 if abs(source['close'][i] - source['open'][i]) > 0.5 * (source['high'][i] - source['low'][i]) else 0)

	source['STR_CANDLE'] = str_candle

	return source

#
# print(datetime.now())
# source = pd.read_csv('bmf/DOL$NM5.csv')[-60000:].reset_index()  # 2500 -> 1 mês
# source = source.drop(columns="index")
#
# source = classification(source, 12)
#
# # source = source.join(pd.Series(vwap(source), name='VWAP'))
#
# # PRICE
# source = do_uptrend(source, 'close')
#
# print(datetime.now())
# print(len(list(source)))
# print('BBANDS')
# # BBANDS
# source = bbands(source, [9, 14, 20, 26], [1., 1.5, 2., 2.5])
#
# print(datetime.now())
# print(len(list(source)))
# print('SMA')
# # SMAs
# source = averages(source, 'SMA', [2, 3, 5, 9, 14, 20, 26, 50, 80, 100, 200], 'close')
#
# print(datetime.now())
# print('EMA')
# # EMAs
# source = averages(source, 'EMA', [2, 3, 5, 9, 14, 26, 72], 'close')
#
# print(datetime.now())
# print('WMA')
# # WMA
# source = averages(source, 'WMA', [2, 3, 5, 9, 14, 26, 72], 'close')
#
# print(datetime.now())
# print(len(list(source)))
# print('KAMA')
# # KAMA
# source = averages(source, 'KAMA', [2, 3, 5, 9, 14, 26, 72], 'close')
#
# print(datetime.now())
# print(len(list(source)))
# print('TEMA')
# # KAMA
# source = averages(source, 'TEMA', [2, 3, 5, 9, 14, 26, 72], 'close')
#
# print(datetime.now())
# print(len(list(source)))
# print('VOLUME')
# # MAs of VOLUME
# source = averages(source, 'SMA', [2, 3, 5, 9, 14, 20, 26, 50, 80, 100, 200], 'volume')
# # source = averages(source, 'EMA', [3, 5, 9, 14, 20, 26, 50, 72], 'volume')
# # source = averages(source, 'WMA', [3, 5, 9, 14, 20, 26, 50, 72], 'volume')
#
# print(datetime.now())
# print(len(list(source)))
# print('DMI')
# # DMI
# dmi_list = [2, 3, 5, 9, 14, 20, 26]
# for i in range(len(dmi_list)):
# 	for j in range(i + 1, len(dmi_list)):
# 		source = dmi(source, dmi_list[i], dmi_list[j])
#
# didi_types = ['SMA', 'EMA', 'WMA']
# print(datetime.now())
# print(len(list(source)))
# print('DIDI')
# # DIDI
# didi_list1 = [2, 3]
# didi_list2 = [9]
# didi_list3 = [14, 20, 26]
#
# for i in didi_list1:
# 	for j in didi_list2:
# 		for k in didi_list3:
# 			for type in didi_types:
# 				source = didi(source, i, j, k, type)
#
# print(datetime.now())
# print(len(list(source)))
# print('SUPER DIDI')
# # HiLo
# for type in didi_types:
# 	source = super_didi(source, 3, 9, 14, 20, type)
#
# print(datetime.now())
# print(len(list(source)))
# print('HILO')
# # HiLo
# for type in didi_types:
# 	source = hilo(source, type, [3, 4, 5, 9, 14])
#
# print(datetime.now())
# print(len(list(source)))
# print('STOCH')
# # STOCH
# stoch_p = [14, 9, 5, 3, 2]
# for i in range(len(stoch_p)):
# 	for j in range(i + 1, len(stoch_p)):
# 		source = stoch(source, stoch_p[i], stoch_p[j])
#
# print(datetime.now())
# print(len(list(source)))
# print('RSI')
# # RSI
# rsi_p = [2, 3, 5, 9, 14]
# source = rsi(source, rsi_p)
#
# print(datetime.now())
# print(len(list(source)))
# print('TRIX')
# # TRIX
# trix_p = [2, 3, 5, 9, 14]
# source = trix(source, trix_p)
#
# # FUTUROS >>>>>>>
#
# # VWAP			> ?
#
# # PARABOLIC SAR > https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/overlap_studies.md
#
# # AROON			> https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/momentum_indicators.md
# # AROON OSC
# # BOP
# # CCI
# # CHANDE
# # MACD
# # MONEY FLOW
# # MOMENTUM
# # WILLIAMS
#
# # OBV			> https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/volume_indicators.md
#
# # CANDLES		> https://github.com/mrjbq7/ta-lib/blob/master/docs/func_groups/pattern_recognition.md
# print(datetime.now())
# print(len(list(source)))
# print("CANDLES")
# source = candles(source)
# source = str_candles(source)
#
# source = source.loc[200:].reset_index().drop(columns="index")
# source = source.dropna()
# source = source.drop(columns=["Date", "close", "open", "high", "low", "Quantity", "volume"])
#
# label = []
# ant = 1
#
# for idx, d in source.iterrows():
# 	value = 2 if d['IS_BOTTOM'] == 1 else 3 if d['IS_TOP'] == 1 else 1
# 	if ant != 1:
# 		label.append(ant)
# 	else:
# 		label.append(value)
# 	ant = value
#
#
# source = source.drop(columns=['IS_TOP', 'IS_BOTTOM'])
#
# # DUPLICAR DADOS
# print(datetime.now())
# print(len(list(source)))
# print("DUPLICAR")
# count = 0
# for column in list(source):
# 	count += 1
# 	if count % 100 == 0:
# 		print(column)
# 	copy = pd.Series((source[column][1:].reset_index(drop=True)).astype('int'), name=column + "[1]")
# 	source = source.join(copy)
#
# source['Label'] = label
#
# source = source.dropna()
# print("SAVE")
# source.to_csv('final_datasets/DOL_60k_duo.csv')
