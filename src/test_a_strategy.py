from scipy.signal import savgol_filter
import numpy as np
import pandas as pd
import warnings
import ccxt
warnings.filterwarnings("ignore")


# read data
exchange = ccxt.binance()
bars = exchange.fetch_ohlcv('ADA/USDT', timeframe='1m', )  # since = (1621123200000)
df = pd.DataFrame(bars[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
# print(df)

all_closes = df['close'].tolist()

for i in range(len(all_closes) + 1):
    closes = all_closes[:i]