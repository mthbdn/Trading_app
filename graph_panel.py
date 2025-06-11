import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from logic.binance_api import get_klines
from logic.utils import utc_to_fr_time
import threading

# Importe le WebSocket si tu en as besoin pour le prix en live
try:
    from logic.binance_ws import BinanceLivePriceStream
    LIVE_WS_AVAILABLE = True
except ImportError:
    BinanceLivePriceStream = None
    LIVE_WS_AVAILABLE = False

class GraphPanel(ctk.CTkFrame):
    def __init__(self, master, client, history_panel=None):
        super().__init__(master)
        self.client = client
        self.symbol = "BTCUSDT"
        self.interval = "1h"
        self.limit = 100
        self.history_panel = history_panel
        self.last_trade_marker = None

        ctk.CTkLabel(self, text="Graphique de la paire", font=("Arial", 16)).pack(anchor="w", pady=(5,0), padx=5)

        # Menu déroulant pour changer l'intervalle
        self.interval_menu = ctk.CTkOptionMenu(
            self,
            values=["1m", "5m", "15m", "1h", "4h", "1d"],
            command=self.set_interval
        )
        self.interval_menu.set(self.interval)
        self.interval_menu.pack(anchor="w", padx=5, pady=(0,5))

        if LIVE_WS_AVAILABLE:
            self.price_label = ctk.CTkLabel(self, text="Prix en temps réel : ---")
            self.price_label.pack(anchor="w", padx=5, pady=(0,5))

        self.refresh_btn = ctk.CTkButton(self, text="Rafraîchir", command=self.refresh_graph_threaded)
        self.refresh_btn.pack(anchor="e", padx=5, pady=(0,5))

        self.fig = Figure(figsize=(7,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.ws_stream = None
        if LIVE_WS_AVAILABLE:
            self.ws_stream = BinanceLivePriceStream(self.symbol, self.on_live_price)
            self.ws_stream.start()

        # Plus de refresh auto ici pour limiter le risque de ban
        self.refresh_graph_threaded()

    def set_interval(self, interval):
        self.interval = interval
        self.refresh_graph_threaded()

    def refresh_graph_threaded(self):
        threading.Thread(target=self.plot_price, daemon=True).start()

    def plot_price(self):
        symbol = self.symbol
        interval = self.interval
        try:
            times, closes = get_klines(self.client, symbol, interval=interval, limit=self.limit)
        except Exception as e:
            self.ax.clear()
            self.ax.set_title(f"Erreur API : {e}")
            self.fig.tight_layout()
            self.canvas.draw()
            return
        self.ax.clear()
        if not closes or not times:
            self.ax.set_title(f"Aucune donnée pour {symbol}")
        else:
            xlabels = [utc_to_fr_time(t) for t in times]
            self.ax.plot(range(len(closes)), closes, label=symbol)
            self.ax.set_xticks(range(0, len(xlabels), max(1, len(xlabels)//8)))
            self.ax.set_xticklabels(xlabels[::max(1, len(xlabels)//8)], rotation=30, fontsize=8)
            self.ax.set_title(f"{symbol} - {interval} (heure française)")
            self.ax.set_xlabel("Date/Heure (FR)")
            self.ax.set_ylabel("Prix")
            self.ax.legend()
            if self.last_trade_marker:
                idx, side = self.last_trade_marker
                color = "green" if side == "BUY" else "red"
                if 0 <= idx < len(closes):
                    self.ax.scatter([idx], [closes[idx]], color=color, s=80, marker="o", zorder=5)
        self.fig.tight_layout()
        self.canvas.draw()

    def on_live_price(self, price):
        if hasattr(self, "price_label"):
            self.after(0, lambda: self.price_label.configure(text=f"Prix en temps réel : {price} USDT"))

    def set_symbol(self, symbol):
        self.symbol = symbol
        if LIVE_WS_AVAILABLE and self.ws_stream:
            self.ws_stream.stop()
            self.ws_stream = BinanceLivePriceStream(self.symbol, self.on_live_price)
            self.ws_stream.start()
        self.refresh_graph_threaded()

    def destroy(self):
        if LIVE_WS_AVAILABLE and self.ws_stream:
            self.ws_stream.stop()
        super().destroy()