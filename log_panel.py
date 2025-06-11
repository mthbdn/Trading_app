import customtkinter as ctk

class LogPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Logs & Console", font=("Arial", 14)).pack(anchor="w", padx=5, pady=(5,0))
        self.textbox = ctk.CTkTextbox(self, width=350, height=200)
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        self.textbox.insert("end", f"{message}\n")
        self.textbox.see("end")