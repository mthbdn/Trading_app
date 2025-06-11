import customtkinter as ctk
import threading
from logic.pnl import get_open_positions_and_pnl
from logic.binance_ws import BinanceLivePriceStream
import time

class OpenPositionsPanel(ctk.CTkFrame):
    def __init__(self, master, client):
        super().__init__(master)
        self.client = client
        ctk.CTkLabel(self, text="Positions ouvertes (PnL temps réel)", font=("Arial", 14)).pack(anchor="w", padx=5, pady=(5,0))
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=(0,5))
        self.position_data = []  # Liste de dicts, chaque dict = une position
        self.price_streams = {}  # symbol => BinanceLivePriceStream
        self.last_prices = {}    # symbol => last live price string
        self.after(100, self.refresh_positions_threaded)

    def refresh_positions_threaded(self):
        threading.Thread(target=self.refresh_positions, daemon=True).start()

    def refresh_positions(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        try:
            positions = get_open_positions_and_pnl(self.client)
        except Exception as e:
            msg = str(e)
            if "1003" in msg or "-1003" in msg:
                msg = "Erreur Binance 1003 : Limite de requêtes dépassée, WebSocket prioritaire pour le live."
            self.after(0, lambda err=msg: ctk.CTkLabel(self.content_frame, text=f"Erreur API : {err}").pack(anchor="w"))
            # On ne relance REST que dans 5 minutes si on est banni
            self.after(300000, self.refresh_positions_threaded)
            return

        self.position_data = positions or []
        symbols = set(pos['symbol'].upper() for pos in self.position_data)

        # Démarre/arrête les flux WebSocket pour chaque symbole
        for sym in list(self.price_streams):
            if sym not in symbols:
                self.price_streams[sym].stop()
                del self.price_streams[sym]
                if sym in self.last_prices:
                    del self.last_prices[sym]

        for sym in symbols:
            if sym not in self.price_streams:
                # Lance un flux WebSocket
                self.price_streams[sym] = BinanceLivePriceStream(sym, lambda price, s=sym: self.on_live_price(s, price))
                self.price_streams[sym].start()

        # Affiche la liste, le prix sera MAJ par on_live_price
        self.after(0, self.display_positions)

        # Rafraîchit l'état complet toutes les 3 minutes (REST)
        self.after(180000, self.refresh_positions_threaded)

    def on_live_price(self, symbol, price):
        # Met à jour le dernier prix reçu pour ce symbole
        self.last_prices[symbol] = float(price)
        self.after(0, self.display_positions)

    def display_positions(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        if not self.position_data:
            ctk.CTkLabel(self.content_frame, text="Aucune position ouverte").pack(anchor="w")
            return
        for pos in self.position_data:
            sym = pos['symbol'].upper()
            qty = pos['qty']
            buy = pos['buy_price']
            last = self.last_prices.get(sym, pos['last_price'])  # Utilise le prix live si dispo, sinon REST
            try:
                pnl = (float(last) - float(buy)) * float(qty)
            except Exception:
                pnl = 0.0
            txt = (
                f"{sym} | Qte: {qty} | Achat: {buy:.4f} "
                f"| Dernier: {float(last):.4f} | PnL: {pnl:.2f} $"
            )
            fg = "green" if pnl > 0 else "red"
            ctk.CTkLabel(self.content_frame, text=txt, text_color=fg).pack(anchor="w")

    def destroy(self):
        for stream in self.price_streams.values():
            stream.stop()
        super().destroy()