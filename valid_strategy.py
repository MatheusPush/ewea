import pandas as pd, talib as tb, numpy as np
import indicators_builder as bd
from setups import close_position


dire = 'data'
filename = 'BIDI4Daily'
stop_entry_dist, stop_loss_dist = 0.01, 0.01
ema_p = 9
side = 'buy'
verbose = True

data = pd.read_csv(f'{dire}/{filename}.csv')

data[f'EMA{ema_p}'] = tb.EMA(data['Close'], ema_p)
data = data.round(2)
uptrend = pd.Series(data['EMA9'][1:].reset_index(drop=True) >= data['EMA9'][:-1].reset_index(drop=True),
					name='EMA9UP')
uptrend.index = data.index[1:]
data = data.join(uptrend)
data.dropna(inplace=True)

# BONUS
data = bd.averages(data, 'SMA', [7], 'Close')
data = bd.hilo(data, 'SMA', [5, 9])
data = bd.stoch(data, 14, 9)

# IDENTIFIERS
data['REF'] = [np.nan] * len(data)
data['SIGNAL'] = [np.nan] * len(data)

papers = []
ref_idx = 0
signal_idx = 0
stop_at = 0

for i in range(1, len(data)):
	yst = data.iloc[i - 1]
	now = data.iloc[i]
	if side == 'buy':
		if signal_idx and now['High'] >= data.loc[signal_idx, 'High'] + stop_entry_dist:
			if data.loc[signal_idx, 'SMA_HI_9_UP'] > 0.5 and \
					data.loc[signal_idx, 'Close_SMA_7_UP'] > 0.5 and \
					data.loc[signal_idx, 'STOCH_14FAST_9SLOW_TYPE0_%D_UP'] > 0.5 and \
					data.loc[signal_idx, 'SMA_LO_5_UP'] > 0.5:
				order_price = round(data.loc[signal_idx, "High"] + stop_entry_dist, 2)
				papers.append({'ref_idx': ref_idx, 'signal_idx': signal_idx, 'order_price': order_price})
				stop_at = round(data.loc[ref_idx + 1:signal_idx, 'Low'].min() - stop_loss_dist, 2)
				ref_idx, signal_idx = 0, 0
				if verbose:
					print(f'COMPROU A {order_price} COM STOP A {stop_at}')
			else:
				ref_idx, signal_idx = 0, 0
		elif stop_at and now['Low'] <= stop_at:
			if verbose:
				print(f'STOPPED A {stop_at}')
			data = close_position(data, papers, stop_at)
			stop_at = 0
			papers = []
		elif now['EMA9UP']:
			if not ref_idx and yst['Low'] <= now['Close'] < yst['Close']:
				ref_idx = yst.name
				if verbose:
					print(f'TEMOS UM REF >> N{now["Close"]} Y(REF){yst["Close"]}')
			elif ref_idx and now['Close'] < data.loc[ref_idx, 'Close']:
				signal_idx = now.name
				if verbose:
					print(f'SINAL EM >> N{now["High"]}')
		else:
			if papers:
				stop_at = round(now['Low'] - stop_loss_dist, 2)
				if verbose:
					print(f'NOVO STOP A {stop_at}')
			ref_idx, signal_idx = 0, 0

if verbose:
	res = round(data['SIGNAL'].sum(), 2)
	print(f'# stop_entry_dist: {stop_entry_dist} / stop_loss_dist: {stop_loss_dist}')
	print(f'# RESULTADO FINAL: {res}\n\n')
	print(data['SIGNAL'].describe())

data.drop(columns=["EMA9", "EMA9UP"], inplace=True)

data = data.dropna(subset=['SIGNAL'])
data['TARGET_BIN'] = data['SIGNAL'].apply(lambda x: 1 if x > 0 else 0)
print(data['TARGET_BIN'].value_counts())
