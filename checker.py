import requests
import urllib.parse


def check_email_api(email):
    """Interroga l'API di XposedOrNot.

    Restituisce una tupla: (stringa_esito, lista_leaks).
    """
    email_normalizzata = email.strip().lower()
    email_pulita = urllib.parse.quote(email_normalizzata)
    url = f"https://api.xposedornot.com/v1/check-email/{email_pulita}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            dati = response.json()
            breaches = []

            if isinstance(dati, list):
                breaches = dati
            elif isinstance(dati, dict):
                summary = dati.get("BreachesSummary", {})
                if isinstance(summary, dict):
                    breaches = summary.get("Breach", [])
                if not breaches:
                    breaches = dati.get("breaches", dati.get("breach", []))

            # Se non ha trovato nulla nei sotto-dizionari, usa i dati radice
            if not breaches and isinstance(dati, list):
                breaches = dati

            nomi_leaks = []
            if breaches:
                for b in breaches:
                    if isinstance(b, dict) and "BreachName" in b:
                        nomi_leaks.append(b["BreachName"])
                    elif isinstance(b, str):
                        nomi_leaks.append(b)
                    else:
                        nomi_leaks.append(str(b))

            # --- IL FIX CRUCIALE ---
            # Se la lista ha un solo elemento ma contiene virgole (es. ["Adobe, Canva"]),
            # la spezziamo in una vera lista pulita.
            lista_leaks_effettiva = []
            for item in nomi_leaks:
                if "," in item:
                    # Dividiamo per virgola, puliamo gli spazi e aggiungiamo
                    parti = [p.strip() for p in item.split(",") if p.strip()]
                    lista_leaks_effettiva.extend(parti)
                else:
                    if item.strip():
                        lista_leaks_effettiva.append(item.strip())

            if lista_leaks_effettiva:
                return (
                    f"⚠️ {email} -> COMPROMESSA in {len(lista_leaks_effettiva)} violazioni!",
                    lista_leaks_effettiva,
                )
            else:
                return (
                    f"⚠️ {email} -> COMPROMESSA (Dati parziali)",
                    ["Unknown_Leak"],
                )

        elif response.status_code == 404:
            return f"✅ {email} -> OK (Sicura)", []
        else:
            return (
                f"❌ {email} -> Errore API (Codice: {response.status_code})",
                [],
            )

    except requests.exceptions.Timeout:
        return f"❌ {email} -> Errore: Timeout server", []
    except Exception as e:
        return f"❌ {email} -> Errore di connessione: {str(e)}", []