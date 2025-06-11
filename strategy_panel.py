import customtkinter as ctk
from logic.strategies.rsi import rsi_signal
from logic.strategies.ma import moving_average_cross
from logic.strategies.bollinger import bollinger_signal
from logic.binance_api import get_klines

class StrategyPanel(ctk.CTkFrame):
    def __init__(self, master, client, graph_panel=None, order_panel=None):
        super().__init__(master)
        self.client = client  # Doit être un objet Binance Client, pas une liste !
        self.graph_panel = graph_panel
        self.order_panel = order_panel

        self.strategy_options = ["RSI", "MA", "BOLLINGER"]
        self.strategy_var = ctk.StringVar(value="RSI")

        ctk.CTkLabel(self, text="Stratégie :").pack(anchor="w", pady=(10,0), padx=5)
        ctk.CTkOptionMenu(self, variable=self.strategy_var, values=self.strategy_options, command=self.update_params).pack(fill="x", padx=5)

        self.period_var = ctk.StringVar(value="14")
        self.period_label = ctk.CTkLabel(self, text="Période principale :")
        self.period_label.pack(anchor="w", pady=(10,0), padx=5)
        self.period_entry = ctk.CTkEntry(self, textvariable=self.period_var)
        self.period_entry.pack(fill="x", padx=5)

        self.period2_var = ctk.StringVar(value="28")
        self.period2_label = ctk.CTkLabel(self, text="Période secondaire (MA) :")
        self.period2_entry = ctk.CTkEntry(self, textvariable=self.period2_var)

        self.stddev_var = ctk.StringVar(value="2")
        self.stddev_label = ctk.CTkLabel(self, text="Écart-type (Bollinger) :")
        self.stddev_entry = ctk.CTkEntry(self, textvariable=self.stddev_var)

        self.intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
        self.interval_var = ctk.StringVar(value="1h")
        ctk.CTkLabel(self, text="Intervalle de temps :").pack(anchor="w", pady=(8,0), padx=5)
        ctk.CTkOptionMenu(self, variable=self.interval_var, values=self.intervals, command=self.on_interval_change).pack(fill="x", padx=5)

        self.refresh_time_var = ctk.StringVar(value="10")
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", pady=5, padx=5)
        ctk.CTkLabel(frame, text="Rafraîchissement auto (s):").pack(side="left", padx=(0,3))
        self.refresh_entry = ctk.CTkEntry(frame, textvariable=self.refresh_time_var, width=40)
        self.refresh_entry.pack(side="left", padx=(0,3))
        self.auto_refresh_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(frame, text="Auto", variable=self.auto_refresh_var, command=self.toggle_auto_refresh).pack(side="left", padx=(2,0))

        ctk.CTkButton(self, text="Analyser maintenant", command=self.run_strategy).pack(pady=5, padx=5, fill="x")
        self.result_label = ctk.CTkLabel(self, text="")
        self.result_label.pack(pady=5, padx=5, fill="x")

        self.after_id = None
        self.update_params()
        self.schedule_auto_refresh()

    def update_params(self, *args):
        strat = self.strategy_var.get()
        self.period2_label.pack_forget()
        self.period2_entry.pack_forget()
        self.stddev_label.pack_forget()
        self.stddev_entry.pack_forget()
        if strat == "MA":
            self.period2_label.pack(anchor="w", pady=(8,0), padx=5)
            self.period2_entry.pack(fill="x", padx=5)
        elif strat == "BOLLINGER":
            self.stddev_label.pack(anchor="w", pady=(8,0), padx=5)
            self.stddev_entry.pack(fill="x", padx=5)

    def on_interval_change(self, *_):
        self.run_strategy()
        if self.graph_panel:
            symbol = self.get_symbol()
            interval = self.interval_var.get()
            self.graph_panel.set_interval(interval)
            self.graph_panel.set_symbol(symbol)
            self.graph_panel.plot_price()

    def get_symbol(self):
        try:
            if self.order_panel and hasattr(self.order_panel, 'symbol_var'):
                return self.order_panel.symbol_var.get()
        except Exception:
            pass
        return "BTCUSDT"

    def run_strategy(self):
        symbol = self.get_symbol()
        interval = self.interval_var.get()
        try:
            times, closes = get_klines(self.client, symbol, interval=interval, limit=100)
        except Exception as e:
            self.result_label.configure(text=f"Erreur API : {e}")
            return
        strat = self.strategy_var.get()
        result = ""
        try:
            period = int(self.period_var.get())
        except Exception:
            self.result_label.configure(text="Période invalide")
            return
        if not closes:
            self.result_label.configure(text="Pas de données")
            return
        if strat == "RSI":
            result = rsi_signal(closes, period=period)
            self.result_label.configure(text=f"RSI ({period}) Signal : {result}")
        elif strat == "MA":
            try:
                period2 = int(self.period2_var.get())
            except Exception:
                self.result_label.configure(text="Période secondaire invalide")
                return
            result = moving_average_cross(closes, fast_period=period, slow_period=period2)
            self.result_label.configure(text=f"MA ({period}/{period2}) Signal : {result}")
        elif strat == "BOLLINGER":
            try:
                std = float(self.stddev_var.get())
            except Exception:
                self.result_label.configure(text="Écart-type invalide")
                return
            result = bollinger_signal(closes, period=period, stddev=std)
            self.result_label.configure(text=f"Bollinger ({period}, {std}σ) Signal : {result}")
        else:
            self.result_label.configure(text="Stratégie non implémentée")

    def schedule_auto_refresh(self):
        if self.auto_refresh_var.get():
            try:
                delay = int(self.refresh_time_var.get())
            except Exception:
                delay = 10
            self.run_strategy()
            self.after_id = self.after(delay * 1000, self.schedule_auto_refresh)
        else:
            self.after_cancel_refresh()

    def toggle_auto_refresh(self):
        if self.auto_refresh_var.get():
            self.schedule_auto_refresh()
        else:
            self.after_cancel_refresh()

    def after_cancel_refresh(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None