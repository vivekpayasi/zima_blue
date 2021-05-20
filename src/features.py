from ta.trend import MACD, AroonIndicator, EMAIndicator
import pandas as pd
from scipy.signal import savgol_filter
import numpy as np

ticker_data = pd.DataFrame({'close': [1, 2, 3, 4, 5]})

# MACD
macd_df = MACD(pd.Series(ticker_data['close']))
ticker_data['macd_diff'] = macd_df.macd_diff()
ticker_data['macd'] = macd_df.macd()
ticker_data['macd_signal'] = macd_df.macd_signal()

# Aroon indicator
aroon_df = AroonIndicator(ticker_data['close'])
ticker_data['aroon_up'] = aroon_df.aroon_up()
ticker_data['aroon_down'] = aroon_df.aroon_down()
ticker_data['aroon_indicator'] = aroon_df.aroon_indicator()

# Exponential Moving Averages
# TODO: Find out window lenghts for EMA
ema_df = EMAIndicator(ticker_data['close'], 12)
ticker_data['ema_12'] = ema_df.ema_indicator()
ema_df = EMAIndicator(ticker_data['close'], 26)
ticker_data['ema_26'] = ema_df.ema_indicator()

# Moving Averages
ticker_data['ma_50'] = ticker_data['close'].rolling(50).mean()
ticker_data['ma_200'] = ticker_data['close'].rolling(200).mean()
ticker_data['ma_7'] = ticker_data['close'].rolling(7).mean()

# Smoothing Features
#   Savgol Filter
ticker_data['savgol_filter'] = savgol_filter(ticker_data['close'].tolist(), 101, 3)

