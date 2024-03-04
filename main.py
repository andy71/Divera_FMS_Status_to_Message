import urllib.request
import json
import os
from datetime import datetime
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Erhalte den absoluten Pfad zur aktuellen Datei
current_directory = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(current_directory, 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Die Konfigurationsdatei '{CONFIG_FILE}' existiert nicht.")
        print("Bitte erstellen Sie eine Konfigurationsdatei mit den erforderlichen Informationen.")
        print("Ein Beispiel für die Konfigurationsdatei könnte wie folgt aussehen:")
        print("{")
        print("    \"api_key\": \"YOUR-API-KEY\",")
        print("    \"message_users_fremdschluessel\": \"1000,1001\",")
        print("    \"status_dict\": {")
        print("        ")
        print("    }")
        print("}")
        exit(1)  # Beenden des Skripts mit Fehlercode 1
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def send_push(shortname, message_text, api_key, message_users_fremdschluessel):
    message_titel = "Änderung Fahrzeugstatus " + shortname + "!"
    if message_users_fremdschluessel != "":
        message_url = f"https://app.divera247.com/api/news?title={urllib.parse.quote(message_titel)}&text={urllib.parse.quote(message_text)}&person={message_users_fremdschluessel}&accesskey={api_key}"
        try:
            urllib.request.urlopen(message_url)
            logger.info("Mitteilung erfolgreich versendet.")
        except Exception as e:
            logger.error("Fehler beim Senden der Mitteilung:", e)

    else:
        logger.info("Keine Divera User angegeben. Mitteilung wird nicht versendet.")

def main():
    config = load_config()
    api_key = config["api_key"]
    message_users_fremdschluessel = config["message_users_fremdschluessel"]
    url = f"https://app.divera247.com/api/v2/pull/all?accesskey={api_key}"

    logger.info("Script gestartet.")

    # Status jeder ID speichern
    status_dict = config.get("status_dict", {})
    try:
        with urllib.request.urlopen(url) as response:
            json_data = json.loads(response.read().decode())
            fms_states = json_data["data"]["cluster"]["fms_status"]
            vehicles_data = json_data["data"]["cluster"]["vehicle"]
            for item_id in vehicles_data:
                item = vehicles_data[item_id]
                id = str(item_id)  # ID als Zeichenkette speichern
                name = item["name"]
                shortname = item["shortname"]
                fmsstatus = item["fmsstatus_id"]
                vehicle_state_change_dt = datetime.fromtimestamp(item["fmsstatus_ts"]).strftime('%Y-%m-%d %H:%M:%S')

                # Wenn die ID noch nicht im status_dict ist, füge sie hinzu
                if id not in status_dict:
                    status_dict[id] = fmsstatus
                    logger.info("ID wurde hinzugefügt. Aktueller status_dict:", status_dict)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ID wurde hinzugefügt. Aktueller status_dict:", status_dict)
                else:
                    # Wenn sich der Status ändert, ...
                    if (status_dict[id] != fmsstatus):
                        message = f"Status von Fahrzeug wurde geändert.\nFahrzeugname: {name}\nKurzname: {shortname}\n"
                        message += f"Neuer Status (seit {vehicle_state_change_dt}): {fms_states['items'][str(fmsstatus)]['name']} ({fmsstatus})\n"

                        # Pushnachricht senden
                        send_push(shortname, message, api_key,message_users_fremdschluessel)
                    # Aktualisiere den Status für die ID
                    status_dict[id] = fmsstatus

        # Speichere den Status in der Konfigurationsdatei
        config["status_dict"] = status_dict
        save_config(config)

    except Exception as e:
        logger.error("Fehler beim Abrufen der Daten oder beim Senden der E-Mail:", e)
if __name__ == "__main__":
    main()
    logger.info("Script erfolgreich ausgeführt!")
