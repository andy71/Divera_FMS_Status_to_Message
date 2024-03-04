# Divera FMS Status Änderungen via Divera 24/7 Mitteilung.

Dieses Script ist eine Vereinfachung von Sleepwalker86s Divera_FMS_Status_to_Email (Thx to you Sleepwalker86).

Dieser Fork sendet nur eine Divera Mitteilung an eine User Fremdschlüssel Liste wann immer sich der Fahrzeugstatus ändert.

Kopiert die config-example.json zu config.json und passt die Beispiel Parameter an.

Beispiel Config:

{
    "_comment": "Diese Datei bitte kopieren und entsprechend anpassen bzw. ausfüllen. STATUS_DICT nicht ändern. Anschließend die datei in config.json umbenennen!",
    "api_key": "YOUR-API-KEY",
    "message_users_fremdschluessel": "1000",
    "status_dict": {
    }
}

## Der Cronjob zum starten könnte so aussehen (contab -e):
Alle 5 Min prüfen ob sich ein Fahrzeug Status geändert hat
*/5 * * * * /usr/bin/python3 /home/pi/Divera_FMS/main.py >> /home/pi/Divera_FMS/log.txt 2>&1
