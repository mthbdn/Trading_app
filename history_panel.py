import customtkinter as ctk
import threading
from logic.binance_api import get_real_trade_history, get_all_traded_symbols

class HistoryPanel(ctk.CTkFrame):
    def __init__(self, master, client):
        super().__init__(master)
        self.client = client
        self.label = ctk.CTkLabel(self, text="Historique des transactions", font=("Arial", 14))
        self.label.pack(anchor="w", padx=5, pady=(5,0))

        self.refresh_btn = ctk.CTkButton(self, text="Rafraîchir", command=self.refresh_history_threaded)
        self.refresh_btn.pack(anchor="e", padx=5, pady=(0,5))

        self.info_label = ctk.CTkLabel(
            self, 
            text="Auto-refresh désactivé pour éviter un ban Binance.\nClique sur 'Rafraîchir' pour mettre à jour l'historique.",
            text_color="orange"
        )
        self.info_label.pack(anchor="w", padx=5, pady=(0,5))

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=(0,5))

        self.auto_refresh = False  # Désactive l'auto-refresh pour éviter les bans

        self.banned = False
        self._refreshing = False
        self.refresh_history_threaded()

    def refresh_history_threaded(self):
        if not self._refreshing:
            self._refreshing = True
            threading.Thread(target=self.refresh_history, daemon=True).start()

    def refresh_history(self):
        for w in self.content_frame.winfo_children():
            w.destroy()
        history = []
        try:
            symbols = get_all_traded_symbols(self.client)
            for symbol in symbols:
                history += get_real_trade_history(self.client, symbol=symbol, limit=10)
            history.sort(reverse=True)
            self.banned = False
        except Exception as e:
            msg = str(e)
            if "1003" in msg or "-1003" in msg:
                msg = ("Erreur Binance 1003 : Limite de requêtes dépassée (ban temporaire). "
                       "Veuillez patienter quelques minutes avant de réessayer.")
                self.banned = True
            else:
                self.banned = False
            self.after(0, lambda: ctk.CTkLabel(self.content_frame, text=f"Erreur API : {msg}", text_color="red").pack(anchor="w"))
            self._refreshing = False
            return

        if not history:
            self.after(0, lambda: ctk.CTkLabel(self.content_frame, text="Aucune transaction trouvée").pack(anchor="w"))
        else:
            def display_history():
                for t in history[:30]:
                    time, side, symbol, price, qty, id_ = t
                    txt = f"{symbol} | {side} | {qty}@{price} | ID: {id_}"
                    ctk.CTkLabel(self.content_frame, text=txt, anchor="w").pack(anchor="w")
            self.after(0, display_history)

        self._refreshing = False
        # Auto-refresh désactivé pour éviter le ban