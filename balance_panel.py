import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from logic.binance_api import get_balances

class BalancePanel(ctk.CTkFrame):
    def __init__(self, master, client):
        super().__init__(master)
        self.client = client

        # Sélection de la devise à afficher
        self.asset_var = ctk.StringVar(value="USDT")
        ctk.CTkLabel(self, text="Évolution du solde", font=("Arial", 14)).pack(anchor="w", padx=5, pady=(5,0))
        ctk.CTkLabel(self, text="Devise :").pack(side="left", padx=(5,0))
        self.asset_menu = ctk.CTkOptionMenu(self, variable=self.asset_var, values=["USDT", "BTC", "ETH"], command=self.update_balance)
        self.asset_menu.pack(side="left", padx=5)
        ctk.CTkButton(self, text="Rafraîchir", command=self.update_balance).pack(side="right", padx=5)

        # Graphique matplotlib
        self.fig = Figure(figsize=(5,2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(10,0))

        # Historique simulé (à remplacer par une vraie base de données ou CSV)
        self.balance_history = {
            "USDT": [1000, 1050, 1020, 1100, 1080],
            "BTC": [0.01, 0.011, 0.012, 0.011, 0.013],
            "ETH": [0.2, 0.21, 0.23, 0.22, 0.25]
        }

        self.update_balance()

    def update_balance(self, *args):
        asset = self.asset_var.get()
        # Ici, tu peux ajouter une vraie récupération historique de solde
        # Pour la démo, on utilise la balance_history simulée
        y = self.balance_history.get(asset, [])
        self.ax.clear()
        if y:
            self.ax.plot(y, marker="o", label=asset)
            self.ax.set_title(f"Solde {asset} dans le temps")
            self.ax.set_ylabel(asset)
            self.ax.legend()
        else:
            self.ax.set_title("Aucun historique pour cette devise.")
        self.fig.tight_layout()
        self.canvas.draw()