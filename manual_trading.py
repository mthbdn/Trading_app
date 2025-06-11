from .binance_api import get_balances, send_order, cancel_open_limit_orders

def manual_trade(client, symbol, side, order_type, quantity, price=None):
    # Passe un ordre, renvoie le résultat
    order = send_order(client, symbol, side, order_type, quantity, price)
    return order

def get_updated_balances(client):
    return get_balances(client)