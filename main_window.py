import customtkinter as ctk
from logic.binance_api import get_client
from gui.order_panel import OrderPanel
from gui.history_panel import HistoryPanel
from gui.open_positions_panel import OpenPositionsPanel
from gui.graph_panel import GraphPanel
from gui.log_panel import LogPanel
from gui.strategy_panel import StrategyPanel

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bot Trading - Interface complète")
        self.geometry("1300x800")

        self.client = get_client()
        self.strategies = ["Scalping", "Swing", "Grid"]  # adapte à tes stratégies
        self.selected_strategy = self.strategies[0]

        # Panneau gauche : Ordre + choix stratégie
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        # Panneau droit : Historique, PnL, Logs
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.pack(side="right", fill="y", padx=10, pady=10)

        # Centre : Graph
        self.center_panel = ctk.CTkFrame(self)
        self.center_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Créer d'abord les panels dont d'autres dépendent
        self.history_panel = HistoryPanel(self.right_panel, self.client)
        self.history_panel.pack(pady=(0, 20), fill="both", expand=True)
        self.pnl_panel = OpenPositionsPanel(self.right_panel, self.client)
        self.pnl_panel.pack(pady=(0, 20), fill="both", expand=True)
        self.log_panel = LogPanel(self.right_panel)
        self.log_panel.pack(fill="both", expand=True)

        self.graph_panel = GraphPanel(self.center_panel, self.client, history_panel=self.history_panel)
        self.graph_panel.pack(fill="both", expand=True, pady=(0, 10))

        self.order_panel = OrderPanel(
            self.left_panel,
            self.client,
            self.get_strategy,
            graph_panel=self.graph_panel,
            history_panel=self.history_panel,
            pnl_panel=self.pnl_panel,
            log_panel=self.log_panel
        )
        self.order_panel.pack(pady=(0, 20), fill="x")

        # Panel stratégie à la fin, car il dépend des autres (graph_panel, order_panel)
        self.strategy_panel = StrategyPanel(self.left_panel, self.client, graph_panel=self.graph_panel, order_panel=self.order_panel)
        self.strategy_panel.pack(pady=(0, 20), fill="x")

    def on_strategy_selected(self, strategy):
        self.selected_strategy = strategy

    def get_strategy(self):
        return self.selected_strategy