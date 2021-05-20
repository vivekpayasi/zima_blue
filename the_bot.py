from scipy.signal import savgol_filter
import pandas as pd
from src import trade
import time
from datetime import datetime

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', None)

import warnings

warnings.filterwarnings("ignore")

from config import config
import ccxt
from ta.trend import MACD  # fast=5, slow=7, signal=4
import websocket
import json
import pprint

SOCKET = 'wss://stream.binance.com:9443/ws/adausdt@kline_1m'
candles_received_count = 0
balance = INITIAL_BALANCE = 12.5
STOPLOSS_THRESHOLD = 0.1  # 10% loss will lead to a stoploss and sell order execution
asset_quantity = 0
TRADE_SYMBOL = 'ADA/USDT'
ORDER_TYPE = 'market'
buying_price = 0
in_position = False
round_trips_count = 0
pending_order = False
limit_order_id = None
PARAMS = {'test': False}

# client = Client(config.API_KEY, config.API_SECRET) #, tld='us'
EXCHANGE = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.API_SECRET,
    'enableRateLimit': True,
    'options': {'adjustForTimeDifference': True}
})

past_candles = EXCHANGE.fetch_ohlcv(TRADE_SYMBOL, timeframe='1m')[:-1]
closes = [i[4] for i in past_candles]
smooth_closes = savgol_filter(closes, 101, 3).tolist()


def on_open(webskt):
    print('connection is opened')


def on_close(webskt):
    print('connection is closed')


def on_message(webskt, message):
    global candles_received_count
    global balance
    global STOPLOSS_THRESHOLD
    global asset_quantity
    global TRADE_SYMBOL
    global ORDER_TYPE
    global closes
    global smooth_closes
    global buying_price
    global in_position
    global round_trips_count
    global pending_order
    global limit_order_id

    global PARAMS
    global EXCHANGE

    # print('receiving msg')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']
    is_candle_closed = candle['x']
    timestamp = candle['t']
    close = candle['c']

    if pending_order:
        print('Checking for the limit order fulfillment.')
        order_info = EXCHANGE.fetchOrder(limit_order_id, symbol=TRADE_SYMBOL)
        order_status = order_info['info']['status']
        if order_status == 'FILLED':
            print('Limit order (SELL) has been fulfilled.')
            balance = order_info['cost']
            sell_price = order_info['average']
            asset_quantity = 0
            pending_order = False
            in_position = False
            round_trips_count += 1
            trade.trip_stats(buying_price, sell_price, balance, asset_quantity)

    if is_candle_closed and not pending_order:
        candles_received_count += 1
        close = float(close)
        timestamp = datetime.utcfromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print('candle {} is closed at {}'.format(candles_received_count, timestamp))
        closes.append(close)
        try:
            smooth_temp = savgol_filter(closes, 175, 3)
            smooth_closes.append(smooth_temp[-1])
            macd_df = MACD(pd.Series(smooth_closes))  # , window_fast=5, window_slow=7, window_sign=4
            histogram = macd_df.macd_diff().tolist()
            if histogram[-1] >= 0 >= histogram[-2]:
                # print('Buying situation')
                if not in_position:
                    print('Placing a BUY order...')
                    # balance, price of ada -> quantity 
                    order_succeeded = trade.place_order(side='buy', quantity=balance / close, symbol=TRADE_SYMBOL,
                                                        order_type=ORDER_TYPE, params=PARAMS, exchange=EXCHANGE)
                    if order_succeeded:
                        print('Succeeded!')
                        in_position = True
                        asset_quantity = asset_quantity + (balance / close)
                        balance = 0
                        buying_price = close
                    else:
                        print('Failed.')
                else:
                    print('Already bought.')

            elif histogram[-1] <= 0 <= histogram[-2]:
                #    Selling situation
                if in_position:
                    # put sell order function call here
                    print('Placing a SELL order...')
                    asset_quantity = float(EXCHANGE.fetch_balance().get('ADA').get('free'))
                    order_succeeded = trade.place_order(side='sell', quantity=asset_quantity, symbol=TRADE_SYMBOL,
                                                        order_type=ORDER_TYPE, params=PARAMS, exchange=EXCHANGE)
                    if order_succeeded:
                        print('Succeeded!')
                        balance = balance + (asset_quantity * close)
                        asset_quantity = 0
                        in_position = False
                        round_trips_count += 1
                        trade.trip_stats(buying_price, close, balance, asset_quantity)
                    else:
                        print('Failed.')

                else:
                    print('Already sold.')
            # STOP LOSS
            if in_position and (close <= buying_price * STOPLOSS_THRESHOLD):
                print('Current price is below the Stoploss Threshold. Selling all the quantity.')
                print('Placing a SELL order...')
                asset_quantity = float(EXCHANGE.fetch_balance().get('ADA').get('free'))
                order_succeeded = trade.place_order(side='sell', quantity=asset_quantity, symbol=TRADE_SYMBOL,
                                                    order_type=ORDER_TYPE, params=PARAMS, exchange=EXCHANGE)
                if order_succeeded:
                    print('Succeeded!')
                    balance = balance + (asset_quantity * close)
                    asset_quantity = 0
                    in_position = False
                    round_trips_count += 1
                    trade.trip_stats(buying_price, close, balance, asset_quantity)
                else:
                    print('Failed.')
        except Exception as e:
            print(e)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
