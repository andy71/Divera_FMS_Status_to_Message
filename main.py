"""
Divera FMS Status Änderungen via Divera 24/7 Mitteilung

Dieses Script ist eine Vereinfachung des Repos Sleepwalker86/Divera_FMS_Status_to_Email
https://github.com/Sleepwalker86/Divera_FMS_Status_to_Email.

Dieser Fork sendet nur noch Divera Mitteilungen an eine Liste von Benutzern (via Fremdschlüssel)
wann immer sich der Fahrzeugstatus ändert.

Darüber hinaus kann die Autoarchivierung genutzt werden um die Mitteilungen nach konfigurierbarer
Zeit in das Archiv zu verschieben.
"""
import urllib.request
import json
import os
import sys
from datetime import datetime
import time
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Erhalte den absoluten Pfad zur aktuellen Datei
current_directory = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(current_directory, 'config.json')
config = None   # pylint: disable=invalid-name

def load_config():
    """
    Lädt die Konfiguration.
    """
    if not os.path.exists(CONFIG_FILE):
        logger.error('Die Konfigurationsdatei "%s" existiert nicht.', CONFIG_FILE)
        logger.info(
            'Bitte erstellen Sie eine Konfigurationsdatei mit den erforderlichen Informationen.\n'
            'Ein Beispiel für die Konfigurationsdatei könnte wie folgt aussehen:\n'
            '{\n'
            '    "api_key": "YOUR-API-KEY",\n'
            '    "StatusLogFile": "vehicle_status.log",\n'
            '    "message_users_fremdschluessel": ["1000","1001"],\n'
            '    "autoarchive_days": 0,\n'
            '    "autoarchive_hours": 0,\n'
            '    "autoarchive_minutes": 0,\n'
            '    "autoarchive_seconds": 0,\n'
            '    "status_dict": {}\n'
            '}\n'
            'Die "autoarchive_*-Einträge ebenso wie der Eintrag "StatusLogFile" sind optional.\n'
            'Die "autoarchive_*-Einträge können beliebig kombiniert und genutzt werden um die '
            'Mitteilung automatisch archivieren zu lassen.\n'
            'Wenn ein StatusLogFile angegeben wird, werden darin die Statusänderungen '
            'aufgezeichnet.\n'
            'Der Pfad dafür kann relativ zum Scriptpfad sein oder ein absoluter Pfad.\n'
            'Statt des Eintrags "message_users_fremdschluessel" kann auch "message_groups_title" '
            'genutzt werden\n'
            'um eine Gruppenbezeichnung anzugeben.\n'
            '    "message_groups_title": ["Ortsbrandmeister", "Gerätewarte"],\n'
            'Es dürfen aber immer nur Gruppen oder nur Benutzer eingetragen werden, niemals beides.'
        )
        sys.exit(1)  # Beenden des Skripts mit Fehlercode 1
    with open(CONFIG_FILE, encoding="utf-8") as f:
        _config = json.load(f)
    return _config


def save_config():
    """
    Speichert die Konfiguration
    """
    with open(CONFIG_FILE, 'w', encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def send_push_v2(
    shortname,
    message_text,
    lat=0, lng=0
):
    """
    Sendet via Divera API eine Push-Nachricht.
    """
    if config["message_users_fremdschluessel"] or config["message_groups_title"]:
        if config["message_users_fremdschluessel"]:
            notification_type = 4
        elif config["message_groups_title"]:
            notification_type = 3
        else:
            logger.info('Keine Divera Empfänger angegeben. Mitteilung wird nicht versendet.')
            return

        if (
            config["autoarchive_days"] or
            config["autoarchive_hours"] or
            config["autoarchive_minutes"] or
            config["autoarchive_seconds"]
        ):
            archive = True
            ts_archive = int(time.time())
            ts_archive += config["autoarchive_seconds"]
            ts_archive += (config["autoarchive_minutes"] * 60)
            ts_archive += (config["autoarchive_hours"] * 60 * 60)
            ts_archive += (config["autoarchive_days"] * 60 * 60 * 24)
        else:
            archive = False
            ts_archive = ''

        body = {
            "News": {
                "title": "Änderung Fahrzeugstatus " + shortname + "!",
                "text": message_text,
                "address": "",
                "lat": lat,
                "lng": lng,
                "survey": False,
                "private_mode": True,
                "notification_type": notification_type,
                "send_push": True,
                "send_sms": False,
                "send_call": False,
                "send_mail": False,
                "send_pager": False,
                "archive": archive,
                "ts_archive": ts_archive,
                "cluster": [],
                "group": config["message_groups_title"],
                "user_cluster_relation": config["message_users_fremdschluessel"]
            },
            "instructions": {
                "group": {
                    "mapping": "title"
                },
                "user_cluster_relation": {
                    "mapping": "foreign_id"
                }
            }
        }
        logger.info(json.dumps(body, indent=4))
        #sys.exit()  # ToDo: zu Testzwecken wird hier beendet
        message_url = f'https://app.divera247.com/api/v2/news?accesskey={config["api_key"]}'
        try:
            req = urllib.request.Request(message_url)
            req.add_header('Content-Type', 'application/json; charset=utf-8')
            jsondataasbytes = json.dumps(body).encode('utf-8')
            req.add_header('Content-Length', len(jsondataasbytes))
            with urllib.request.urlopen(req, jsondataasbytes) as response:
                logger.info("Mitteilung erfolgreich versendet.")
                logger.info(response.read())
        except urllib.error.URLError as e:
            logger.error("Fehler beim Senden der Mitteilung:\n%s", e)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Unbehandelter Fehler beim Senden der Mitteilung:\n%s", e)
    else:
        logger.info("Keine Divera User angegeben. Mitteilung wird nicht versendet.")

def main():
    """
    Hauptfunktion
    """
    global config   # pylint: disable=global-statement
    config = load_config()

    if not 'message_users_fremdschluessel' in config:
        config["message_users_fremdschluessel"] = []

    if not 'message_groups_title' in config:
        config["message_groups_title"] = []

    if config["message_users_fremdschluessel"] and config["message_groups_title"]:
        logger.error('Fehler in der Konfiguration:')
        logger.error(
            'Es können entweder nur Gruppen oder nur Benutzer als Empfänger angegeben werden.'
        )
        sys.exit(1)

    if not 'autoarchive_days' in config:
        config["autoarchive_days"] = 0

    if not 'autoarchive_hours' in config:
        config["autoarchive_hours"] = 0

    if not 'autoarchive_minutes' in config:
        config["autoarchive_minutes"] = 0

    if not 'autoarchive_seconds' in config:
        config["autoarchive_seconds"] = 0

    status_log_file = config.get('StatusLogFile', None)
    if status_log_file:
        if os.path.isabs(config['StatusLogFile']):
            status_log_file = config['StatusLogFile']
        else:
            status_log_file = os.path.join(current_directory, config['StatusLogFile'])
        status_log_file = os.path.abspath(status_log_file)

    url = f'https://app.divera247.com/api/v2/pull/all?accesskey={config["api_key"]}'

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
                vehicle_state_change_dt = datetime.fromtimestamp(
                                                item["fmsstatus_ts"]
                                            ).strftime('%Y-%m-%d %H:%M:%S')

                # Wenn die ID noch nicht im status_dict ist, füge sie hinzu
                if str(item_id) not in status_dict:
                    status_dict[str(item_id)] = item["fmsstatus_id"]
                    logger.info("ID wurde hinzugefügt. Aktueller status_dict: %s", status_dict)
                else:
                    # Wenn sich der Status ändert, ...
                    if status_dict[str(item_id)] != item["fmsstatus_id"]:
                        message = (
                            f'Status von Fahrzeug wurde geändert.\n'
                            f'Fahrzeugname: {item["name"]}\nKurzname: {item["shortname"]}\n'
                        )
                        message += (
                            f'Neuer Status (seit {vehicle_state_change_dt}): '
                            f'{fms_states["items"][str(item["fmsstatus_id"])]["name"]} '
                            f'({item["fmsstatus_id"]})\n'
                        )
                        
                        message += (
                            f'\nPosition:\nhttps://www.google.com/maps/place/{item["lat"]},'
                            f'{item["lng"]}\n'
                        ) if item["lat"] and item["lng"] else ''

                        if status_log_file:
                            with open(status_log_file, 'a', encoding="utf-8") as log:
                                log.write(
                                    f'{vehicle_state_change_dt} - {item["name"]} - '
                                    f'{item["fmsstatus_id"]}\n'
                                )

                        # Pushnachricht senden
                        send_push_v2(
                            shortname=item["shortname"],
                            message_text=message,
                            lat=item["lat"],
                            lng=item["lng"]
                        )
                    # Aktualisiere den Status für die ID
                    status_dict[str(item_id)] = item["fmsstatus_id"]

        # Speichere den Status in der Konfigurationsdatei
        config["status_dict"] = status_dict
        save_config()
    except TypeError as e:
        logger.error("Typfehler beim Abrufen der Daten:\n%s", e)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Unbehandelter Fehler beim Abrufen der Daten:\n%s", e)

if __name__ == "__main__":
    try:
        main()
        logger.info("Script erfolgreich ausgeführt.")
    except TypeError as e:
        logger.error("Typfehler beim Ausführen des Scripts:\n%s", e)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Unbehandelter Fehler beim Ausführen des Scripts:\n%s", e)
        sys.exit(1)
