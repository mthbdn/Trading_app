from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import API_KEY, API_SECRET
import time

# Monkeypatch : on désactive le ping automatique à l'init du client pour éviter le ban direct
def fake_ping(self):
    return {}

Client.ping = fake_ping

def get_client():
    api_key = API_KEY
    api_secret = API_SECRET
    if not api_key or not api_secret:
        raise RuntimeError("Clés API Binance manquantes dans config.py.")
    try:
        client = Client(api_key, api_secret, testnet=True)
        return client
    except BinanceAPIException as e:
        if e.code == -1003:
            import re
            m = re.search(r'banned until (\d+)', str(e))
            if m:
                ban_end = int(m.group(1)) / 1000
                now = time.time()
                wait_sec = int(ban_end - now)
                print(f"Ton IP est bannie par Binance. Réessaie dans {wait_sec//60} minutes.")
            else:
                print("Ton IP est bannie par Binance. Réessaie plus tard.")
            raise
        else:
            raise

def place_order(client, symbol, side, order_type, quantity):
    try:
        return client.create_order(
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity
        )
    except Exception as e:
        return {"error": str(e)}

def get_real_trade_history(client, symbol="BTCUSDT", limit=20):
    try:
        trades = client.get_my_trades(symbol=symbol, limit=limit)
    except BinanceAPIException as e:
        if e.code == -1003:
            raise
        return []
    except Exception as e:
        return []
    history = []
    for t in trades:
        side = "BUY" if t['isBuyer'] else "SELL"
        price = t['price']
        qty = t['qty']
        time_ = t['time']  # timestamp en ms
        history.append((time_, side, symbol, price, qty, t['id']))
    # Trie du plus récent au plus ancien
    history.sort(reverse=True)
    return history

def get_all_traded_symbols(client):
    # Renvoie toutes les paires avec un solde non nul (hors USDT)
    info = client.get_account()
    return [b['asset'] + 'USDT' for b in info['balances'] if float(b['free']) + float(b['locked']) > 0 and b['asset'] != "USDT"]

def get_klines(client, symbol, interval="1h", limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    times = [int(k[0]) for k in klines]
    closes = [float(k[4]) for k in klines]
    return times, closes