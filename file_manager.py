def genera_tabella_grezza(cronologia_esiti, mappa_leaks):
    """Genera un report completo: prima l'elenco dettagliato per ogni email,

    poi l'accorpamento dei leak in comune.
    """
    righe_report = []

    # ==================================================
    # PARTE 1: ELENCO DELLE EMAIL CON I PROPRI LEAK PERSONALI
    # ==================================================
    righe_report.append("==================================================")
    righe_report.append("          1. DETTAGLIO PERSONALE PER EMAIL        ")
    righe_report.append("==================================================")

    for esito in cronologia_esiti:
        righe_report.append(esito)

    righe_report.append("\n")

    # ==================================================
    # PARTE 2: ACCORPAMENTO PER LEAK IN COMUNE
    # ==================================================
    righe_report.append("==================================================")
    righe_report.append("          2. FILTRAGGIO PER LEAK IN COMUNE        ")
    righe_report.append("==================================================")

    if not mappa_leaks:
        righe_report.append(
            "✅ Nessuna compromissione rilevata nei Data Breach monitorati!"
        )
    else:
        leaks_ordinati = sorted(list(mappa_leaks.keys()))
        for leak in leaks_ordinati:
            lista_email = mappa_leaks[leak]

            righe_report.append(f"\n+" + "-" * 60 + "+")
            righe_report.append(
                f"| 🔥 DATA BREACH: {leak.upper().ljust(43)} |"
            )
            righe_report.append(
                f"|    Account colpiti in comune: {str(len(lista_email)).ljust(20)} |"
            )
            righe_report.append("+" + "-" * 60 + "+")

            for email in sorted(lista_email):
                righe_report.append(f"  └── 📧 {email}")

    return "\n".join(righe_report)


def salva_report_lista(nome_file, contenuto_report):
    """Salva il report unico generato."""
    with open(nome_file, "w", encoding="utf-8") as f:
        f.write(contenuto_report)


def salva_report_singolo(nome_file, esito, tabella):
    """Salva il log della singola email (lasciala così com'è)."""
    with open(nome_file, "w", encoding="utf-8") as f:
        f.write("--- REPORT CONTROLLO SINGOLO ---\n")
        f.write(esito + "\n\n")
        f.write(tabella + "\n")