import pandas as pd, talib as tb, numpy as np


def close_position(data, papers, close_price):
	for p in papers:
		result = round((close_price / p['order_price'] - 1) * 100, 2)
		data.loc[p['ref_idx'], 'REF'] = result
		data.loc[p['signal_idx'], 'SIGNAL'] = result
		print(f'>> RESULT: {result}')
	return data


def setup9_3(data, stop_entry_dist, stop_loss_dist, ema_p=9, side='buy', verbose=False):
	data[f'EMA{ema_p}'] = tb.EMA(data['close'], ema_p)
	data = data.round(2)
	uptrend = pd.Series(data['EMA9'][1:].reset_index(drop=True) >= data['EMA9'][:-1].reset_index(drop=True),
						name='EMA9UP')
	uptrend.index = data.index[1:]
	data = data.join(uptrend)
	data.dropna(inplace=True)

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
			if signal_idx and now['high'] >= data.loc[signal_idx, 'high'] + stop_entry_dist:
				order_price = round(data.loc[signal_idx, "high"] + stop_entry_dist, 2)
				papers.append({'ref_idx': ref_idx, 'signal_idx': signal_idx, 'order_price': order_price})
				stop_at = round(data.loc[ref_idx + 1:signal_idx, 'low'].min() - stop_loss_dist, 2)
				ref_idx, signal_idx = 0, 0
				if verbose:
					print(f'COMPROU A {order_price} COM STOP A {stop_at}')
			elif stop_at and now['low'] <= stop_at:
				if verbose:
					print(f'STOPPED A {stop_at}')
				data = close_position(data, papers, stop_at)
				stop_at = 0
				papers = []
			elif now['EMA9UP']:
				if not ref_idx and yst['low'] <= now['close'] < yst['close']:
					ref_idx = yst.name
					if verbose:
						print(f'TEMOS UM REF >> N{now["close"]} Y(REF){yst["close"]}')
				elif ref_idx and now['close'] < data.loc[ref_idx, 'close']:
					signal_idx = now.name
					if verbose:
						print(f'SINAL EM >> N{now["high"]}')
			else:
				if papers:
					stop_at = round(now['low'] - stop_loss_dist, 2)
					if verbose:
						print(f'NOVO STOP A {stop_at}')
				ref_idx, signal_idx = 0, 0

	if verbose:
		res = round(data['SIGNAL'].sum(), 2)
		print(f'# stop_entry_dist: {stop_entry_dist} / stop_loss_dist: {stop_loss_dist}')
		print(f'# RESULTADO FINAL: {res}\n\n')
		print(data['SIGNAL'].describe())

	data.drop(columns=["EMA9", "EMA9UP"], inplace=True)

	return data
