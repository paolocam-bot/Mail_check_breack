import threading
import time
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Importiamo la logica dagli altri file di progetto
from checker import check_email_api
from file_manager import (
    genera_tabella_grezza,
    salva_report_lista,
    salva_report_singolo,
)


class BreachCheckerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Data Breach Checker - Project Edition")
        self.geometry("650x720")
        self.resizable(False, False)

        self.email_list = []

        # --- INTERFACCIA GRAFICA (UI) ---
        self.title_label = ctk.CTkLabel(
            self,
            text="🔒 Email Breach Finder & Tabulator",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.pack(pady=15)

        # SEZIONE 1: Singola Email
        self.single_frame = ctk.CTkFrame(self)
        self.single_frame.pack(pady=8, padx=20, fill="x")

        self.single_label = ctk.CTkLabel(
            self.single_frame,
            text="Controlla una singola email:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.single_label.pack(pady=5, padx=10, anchor="w")

        self.email_entry = ctk.CTkEntry(
            self.single_frame, placeholder_text="Inserisci l'indirizzo email..."
        )
        self.email_entry.pack(pady=5, padx=10, fill="x")

        self.btn_check_single = ctk.CTkButton(
            self.single_frame,
            text="Verifica Email",
            command=self.check_single_email,
        )
        self.btn_check_single.pack(pady=10)

        # SEZIONE 2: Lista da File
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=8, padx=20, fill="x")

        self.file_label = ctk.CTkLabel(
            self.file_frame,
            text="Controlla una lista da file (.txt):",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.file_label.pack(pady=5, padx=10, anchor="w")

        self.btn_load_file = ctk.CTkButton(
            self.file_frame,
            text="Scegli file .txt",
            fg_color="#2c3e50",
            hover_color="#34495e",
            command=self.load_file,
        )
        self.btn_load_file.pack(pady=5)

        self.file_status_label = ctk.CTkLabel(
            self.file_frame, text="Nessun file caricato", font=ctk.CTkFont(size=12)
        )
        self.file_status_label.pack(pady=3)

        self.btn_check_list = ctk.CTkButton(
            self.file_frame,
            text="Avvia Scansione Lista",
            state="disabled",
            fg_color="#005523",
            hover_color="#00a745",
            command=self.start_list_checking_thread,
        )
        self.btn_check_list.pack(pady=10)

        # SEZIONE 3: Area Console e Intestazione Risultati
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(10, 0), padx=20, fill="x")

        self.result_label = ctk.CTkLabel(
            self.header_frame, text="Risultati:", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.result_label.pack(side="left", anchor="w")

        self.btn_clear = ctk.CTkButton(
            self.header_frame,
            text="🧹 Pulisci Log",
            width=100,
            height=24,
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            command=self.clear_log,
        )
        self.btn_clear.pack(side="right", anchor="e")

        self.result_box = ctk.CTkTextbox(self, width=610, height=230)
        self.result_box.pack(pady=10, padx=20)
        self.result_box.configure(state="disabled")

    def log_message(self, message):
        self.result_box.configure(state="normal")
        self.result_box.insert(tk.END, message + "\n")
        self.result_box.see(tk.END)
        self.result_box.configure(state="disabled")

    def clear_log(self):
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", tk.END)
        self.result_box.configure(state="disabled")

    def check_single_email(self):
        email = self.email_entry.get().strip()
        if not email:
            self.log_message("Scegli un'email valida prima di controllare.")
            return

        self.clear_log()
        self.log_message(f"Verifica in corso per {email}...\n")

        def target():
            # CORRETTO: stringa_esito riceve il testo, lista_leaks riceve l'array vero
            stringa_esito, lista_leaks = check_email_api(email)
            
            self.log_message(stringa_esito)

            # Popoliamo correttamente la mappa temporanea
            mappa_leaks = {leak: [email] for leak in lista_leaks}
            
            stringa_tabella = genera_tabella_grezza([stringa_esito], mappa_leaks)
            self.log_message("\n" + stringa_tabella)

            try:
                salva_report_singolo("risultato_singolo.txt", stringa_esito, stringa_tabella)
                self.log_message("\n💾 Report salvato in: risultato_singolo.txt")
            except Exception as e:
                self.log_message(f"❌ Errore salvataggio file: {e}")

        threading.Thread(target=target).start()

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("File di testo", "*.txt")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                self.email_list = [line.strip() for line in file if line.strip()]
            self.file_status_label.configure(
                text=f"Caricate {len(self.email_list)} email con successo!"
            )
            self.btn_check_list.configure(state="normal")
        else:
            self.file_status_label.configure(text="Caricamento annullato.")

    def start_list_checking_thread(self):
        threading.Thread(target=self.check_email_list_logic).start()

    def check_email_list_logic(self):
        self.clear_log()
        self.btn_check_list.configure(state="disabled")
        self.btn_check_single.configure(state="disabled")
        self.btn_load_file.configure(state="disabled")

        total = len(self.email_list)
        self.log_message(f"--- Inizio controllo di {total} email (Delay di 2 secondi) ---\n")

        mappa_leak_globale = {}
        cronologia_esiti = []

        for i, email in enumerate(self.email_list, 1):
            email_corrente = str(email).strip()
            self.log_message(f"[{i}/{total}] Controllo: {email_corrente}...")

            # 1. Chiamiamo l'API: stringa_esito prende il testo, lista_leaks è una VERA lista di Python
            stringa_esito, lista_leaks = check_email_api(email_corrente)
            cronologia_esiti.append(stringa_esito)

            # 2. Controllo di sicurezza: se per qualche motivo l'API ha risposto con una stringa
            # invece di una lista (es. "['Leak1', 'Leak2']"), la convertiamo forzatamente in una vera lista
            if isinstance(lista_leaks, str):
                import ast
                try:
                    lista_leaks = ast.literal_eval(lista_leaks)
                except:
                    lista_leaks = [lista_leaks]

            # 3. Ora cicliamo sui leak REALI. Ognuno sarà una stringa singola (es. "APOLLO")
            for singolo_leak in lista_leaks:
                singolo_leak = str(singolo_leak).strip()
                
                # Rimuoviamo eventuali rimasugli di formattazione testuale errata
                singolo_leak = singolo_leak.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                
                if not singolo_leak or singolo_leak == "Unknown_Leak":
                    continue
                
                # Popoliamo il dizionario inserendo il singolo leak come chiave
                if singolo_leak not in mappa_leak_globale:
                    mappa_leak_globale[singolo_leak] = []
                if email_corrente not in mappa_leak_globale[singolo_leak]:
                    mappa_leak_globale[singolo_leak].append(email_corrente)

            if i < total:
                time.sleep(2)

        # 4. Generiamo il report finale
        report_finale = genera_tabella_grezza(cronologia_esiti, mappa_leak_globale)

        self.clear_log()
        self.log_message(report_finale)

        try:
            salva_report_lista("risultati_scansione.txt", report_finale)
            self.log_message(f"\n--- TERMINATO ---\n💾 Report salvato in: risultati_scansione.txt")
        except Exception as e:
            self.log_message(f"❌ Errore di scrittura su file: {e}")

        self.btn_check_list.configure(state="normal")
        self.btn_check_single.configure(state="normal")
        self.btn_load_file.configure(state="normal")