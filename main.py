import customtkinter as ctk
from gui import BreachCheckerApp

if __name__ == "__main__":
    # Inizializza i temi grafici prima di avviare la finestra
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Istanzia l'applicazione e lancia il loop principale
    app = BreachCheckerApp()
    app.mainloop()