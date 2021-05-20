def place_order(side, quantity, symbol, order_type, params, exchange, price=None):
    try:
        print('Sending order.')
        order = exchange.create_order(side=side, amount=quantity, symbol=symbol, type=order_type, price=price,
                                      params=params)
        limit_order_id = order['info']['orderId']
        print(order)
    except Exception as e:
        print("Error creating order")
        print(e)
        return False, None
    return True, limit_order_id


def place_sell_order(base_currency, qoute_currency, order_type, params, exchange, ):
    # if close >= buying_price:
    print('Placing a SELL order...')
    asset_quantity = float(exchange.fetch_balance().get(base_currency).get('free'))
    order_succeeded = place_order(side='sell', quantity=asset_quantity, symbol=base_currency + '/' + qoute_currency,
                                  order_type=order_type, params=params, exchange=exchange)
    if order_succeeded:
        print('Succeeded!')
        balance = balance + (asset_quantity * close)
        asset_quantity = 0
        in_position = False
        round_trips_count += 1
        trade.trip_stats(buying_price, close, balance, asset_quantity)
    else:
        print('Failed.')
    # else:
    #     print('Current price is lower than buying price,
    #     hence placing a limit order at buying price.')
    #     asset_quantity = float(exchange.fetch_balance().get('ADA').get('free'))
    #     order_succeeded = place_order(side='sell', quantity=asset_quantity,
    #     symbol=TRADE_SYMBOL, order_type='limit', price=buying_price, params=PARAMS, exchange=exchange)
    #     # check if order Succeeded
    #     if order_succeeded:
    #         print('Limit order placing succeeded.')
    #         # assign pending_order as True
    #         pending_order = True


def trip_stats(buying_price, current_price, balance, asset_quantity):
    print('Round trip is complete.')
    print('Buying Price: {} | Selling Price: {}'.format(buying_price, current_price))
    if current_price >= buying_price:
        print('Profit in this round trip: {}%'.format(round(100 * (current_price - buying_price) / buying_price, 2)))
    else:
        print('Loss in this round trip: {}%'.format(round(100 * (buying_price - current_price) / current_price, 2)))
    print('Balance: USDT{} | Asset Quantity: {}'.format(balance, asset_quantity))
