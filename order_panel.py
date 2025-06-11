import customtkinter as ctk
import threading
from logic.binance_api import place_order

class OrderPanel(ctk.CTkFrame):
    def __init__(self, master, client, get_strategy, graph_panel, history_panel, pnl_panel, log_panel):
        super().__init__(master)
        self.client = client
        self.get_strategy = get_strategy  # fonction qui retourne la stratégie sélectionnée
        self.graph_panel = graph_panel
        self.history_panel = history_panel
        self.pnl_panel = pnl_panel
        self.log_panel = log_panel

        ctk.CTkLabel(self, text="Passer un ordre").pack(pady=(0, 10))
        self.symbol_entry = ctk.CTkEntry(self, placeholder_text="Symbole ex : BTCUSDT")
        self.symbol_entry.pack(pady=5)
        self.qty_entry = ctk.CTkEntry(self, placeholder_text="Quantité")
        self.qty_entry.pack(pady=5)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Acheter", fg_color="green", command=self.on_buy).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Vendre", fg_color="red", command=self.on_sell).pack(side="left", padx=5)

        self.status_lbl = ctk.CTkLabel(self, text="")
        self.status_lbl.pack()

    def on_buy(self):
        self._send_order("BUY")

    def on_sell(self):
        self._send_order("SELL")

    def _send_order(self, side):
        symbol = self.symbol_entry.get().upper().strip()
        qty = self.qty_entry.get().strip()
        strategy = self.get_strategy()
        if not symbol or not qty:
            self.status_lbl.configure(text="Complétez tous les champs", text_color="orange")
            return
        self.status_lbl.configure(text="Envoi de l'ordre...", text_color="grey")
        threading.Thread(target=self._place_and_refresh, args=(symbol, side, qty, strategy), daemon=True).start()

    def _place_and_refresh(self, symbol, side, qty, strategy):
        try:
            result = place_order(self.client, symbol, side, "MARKET", float(qty))
            if "error" in result:
                raise Exception(result["error"])
            msg = f"Ordre {side} {qty} {symbol} avec stratégie {strategy} envoyé"
            self.after(0, lambda: self.status_lbl.configure(text=msg, text_color="green"))
            if self.log_panel:
                self.after(0, lambda: self.log_panel.log(msg))
            if self.history_panel:
                self.after(100, self.history_panel.refresh_history_threaded)
            if self.pnl_panel:
                self.after(100, self.pnl_panel.refresh_positions_threaded)
            if self.graph_panel:
                self.after(100, self.graph_panel.refresh_graph_threaded)
        except Exception as e:
            self.after(0, lambda: self.status_lbl.configure(text=f"Erreur : {e}", text_color="red"))
            if self.log_panel:
                self.after(0, lambda: self.log_panel.log(f"Erreur d'ordre: {e}"))