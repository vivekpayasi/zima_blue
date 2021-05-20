import config
import ccxt
import json
import pprint

exchange = ccxt.binance({
    'apiKey': config.API_KEY,
    'secret': config.API_SECRET,
    'enableRateLimit': True,
    'options': {'adjustForTimeDifference': True}
})

symbol = 'ADA/USDT'
order_type = 'limit'  # or 'market'
side = 'sell'  # or 'buy'
amount = 10
price = None  # 0.60154  # or None

# extra params and overrides if needed
params = {
    'test': True,  # test if it's valid, but don't actually place it
}

# Place order
# order = exchange.create_order(symbol, type, side, amount, price, params)
# print(order)

# balance = float(exchange.fetch_balance().get('ADA').get('free'))
# print(balance)

order_info = exchange.fetchOrder('1509719787', symbol=symbol)
pprint.pprint(order_info)
# print(json_order)
