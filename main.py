import urllib.request
import json
import os
from datetime import datetime
import time
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Erhalte den absoluten Pfad zur aktuellen Datei
current_directory = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(current_directory, 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.error(f'Die Konfigurationsdatei "{CONFIG_FILE}" existiert nicht.')
        logger.info('Bitte erstellen Sie eine Konfigurationsdatei mit den erforderlichen Informationen.')
        logger.info('Ein Beispiel für die Konfigurationsdatei könnte wie folgt aussehen:')
        logger.info('{')
        logger.info('    "api_key": "YOUR-API-KEY",')
        logger.info('    "message_users_fremdschluessel": ["1000","1001"],')
        logger.info('    "autoarchive_days": 0,')
        logger.info('    "autoarchive_hours": 0,')
        logger.info('    "autoarchive_minutes": 0,')
        logger.info('    "autoarchive_seconds": 0,')
        logger.info('    "status_dict": {}')
        logger.info('}')
        logger.info('Die "autoarchive_*-Einträge sind optional.')
        logger.info('Sie können beliebig kombiniert und genutzt werden um die Mitteilung automatisch archivieren zu lassen.')
        exit(1)  # Beenden des Skripts mit Fehlercode 1
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def send_push_v2(shortname, message_text, api_key, message_users_fremdschluessel, lat=0, lng=0, autoarchive_days=0, autoarchive_hours=0, autoarchive_minutes=0, autoarchive_seconds=0):
    if message_users_fremdschluessel != "":
        if (autoarchive_days or autoarchive_hours or autoarchive_minutes or autoarchive_seconds):
            archive = True
            ts_archive = int(time.time())
            ts_archive += autoarchive_seconds
            ts_archive += (autoarchive_minutes * 60)
            ts_archive += (autoarchive_hours * 60 * 60)
            ts_archive += (autoarchive_days * 60 * 60 * 24)
        else:
            archive = False
            ts_archive = ''

        body={
            "News": {
                "title": "Änderung Fahrzeugstatus " + shortname + "!",
                "text": message_text,
                "address": "",
                "lat": lat,
                "lng": lng,
                "survey": False,
                "private_mode": True,
                "notification_type": 4,
                "send_push": True,
                "send_sms": False,
                "send_call": False,
                "send_mail": False,
                "send_pager": False,
                "archive": archive,
                "ts_archive": ts_archive,
                "cluster": [],
                "group": [],
                "user_cluster_relation": [
                    message_users_fremdschluessel
                ]
            },
            "instructions": {
                "user_cluster_relation": {
                    "mapping": "foreign_id"
                }
            }
        }
        logger.debug(json.dumps(body, indent=4))

        message_url = f"https://app.divera247.com/api/v2/news?accesskey={api_key}"
        try:
            req = urllib.request.Request(message_url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            jsondataasbytes = json.dumps(body).encode('utf-8')
            req.add_header('Content-Length', len(jsondataasbytes))
            print("foo")
            response = urllib.request.urlopen(req, jsondataasbytes)
            logger.info("Mitteilung erfolgreich versendet.")
            logger.info(response.read())
        except Exception as e:
            logger.error("Fehler beim Senden der Mitteilung:")
            logger.error(e)
    else:
        logger.info("Keine Divera User angegeben. Mitteilung wird nicht versendet.")

def main():
    config = load_config()
    api_key = config["api_key"]
    message_users_fremdschluessel = config["message_users_fremdschluessel"]
    if 'autoarchive_days' in config:
        autoarchive_days = config['autoarchive_days']
    else:
        autoarchive_days = 0
    if 'autoarchive_hours' in config:
        autoarchive_hours = config['autoarchive_hours']
    else:
        autoarchive_hours = 0
    if 'autoarchive_minutes' in config:
        autoarchive_minutes = config['autoarchive_minutes']
    else:
        autoarchive_minutes = 0
    if 'autoarchive_seconds' in config:
        autoarchive_seconds = config['autoarchive_seconds']
    else:
        autoarchive_seconds = 0

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
                lat= item["lat"]
                lng= item["lng"]
                vehicle_state_change_dt = datetime.fromtimestamp(item["fmsstatus_ts"]).strftime('%Y-%m-%d %H:%M:%S')

                # Wenn die ID noch nicht im status_dict ist, füge sie hinzu
                if id not in status_dict:
                    status_dict[id] = fmsstatus
                    logger.info(f"ID wurde hinzugefügt. Aktueller status_dict: {status_dict}")
                else:
                    # Wenn sich der Status ändert, ...
                    if (status_dict[id] != fmsstatus):
                        message = f"Status von Fahrzeug wurde geändert.\nFahrzeugname: {name}\nKurzname: {shortname}\n"
                        message += f"Neuer Status (seit {vehicle_state_change_dt}): {fms_states['items'][str(fmsstatus)]['name']} ({fmsstatus})\n"
                        if (lat and lng):
                            message += f"\nPosition: {lat}, {lng}"

                        # Pushnachricht senden
                        send_push_v2(
                            shortname,
                            message,
                            api_key,
                            message_users_fremdschluessel,
                            lat=lat,
                            lng=lng,
                            autoarchive_days=autoarchive_days,
                            autoarchive_hours=autoarchive_hours,
                            autoarchive_minutes=autoarchive_minutes,
                            autoarchive_seconds=autoarchive_seconds
                        )
                    # Aktualisiere den Status für die ID
                    status_dict[id] = fmsstatus

        # Speichere den Status in der Konfigurationsdatei
        config["status_dict"] = status_dict
        save_config(config)
    except Exception as e:
        logger.error("Fehler beim Abrufen der Daten:\n", e)

if __name__ == "__main__":
    try:
        main()
        logger.info("Script erfolgreich ausgeführt.")
    except Exception as e:
        logger.error("Fehler beim Ausführen des Scripts:\n", e)
        exit(1)
