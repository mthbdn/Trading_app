import websocket
import threading
import json
import time

class BinanceLivePriceStream:
    def __init__(self, symbol, on_price, reconnect_delay=10):
        self.symbol = symbol.lower()
        self.on_price = on_price  # callback(price_str)
        self.reconnect_delay = reconnect_delay
        self.ws = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._stop.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self.ws:
            self.ws.close()

    def _run(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        while not self._stop.is_set():
            try:
                self.ws = websocket.WebSocketApp(
                    url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self.ws.on_open = self._on_open
                self.ws.run_forever()
            except Exception as e:
                print(f"WebSocket erreur: {e}")
            if not self._stop.is_set():
                time.sleep(self.reconnect_delay)

    def _on_message(self, ws, message):
        data = json.loads(message)
        price = data.get('p')
        if price and self.on_price:
            self.on_price(price)

    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, *args):
        print("WebSocket closed")

    def _on_open(self, ws):
        print("WebSocket opened for", self.symbol)