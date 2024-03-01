# Divera FMS Status per Email oder Divera 24/7 Mitteilung senden bei Wechsel von ungleich 6 -> 6 oder 6 -> ungleich 6.

Dieses Script sendet eine Email oder eine Divera Mitteilung an eine E-Mail Empfängerliste, eine User Fremdschlüssel Liste oder eine RIC Liste wenn der Status sich von ungleich 6 -> 6 oder von 6 -> ungleich 6 ändert.

Kopiert die config-example.json zu config.json und passt die Beispiel Parameter an.

Beispiel Config:

{
    "_comment": "Diese Datei bitte kopieren und entsprechend anpassen bzw. ausfüllen. STATUS_DICT nicht ändern. Anschließend die datei in config.json umbenennen!",
    "api_key": "YOUR-API-KEY",
    "sender_email": "sender@example.de",
    "email_password": "YOUR-EMAIL-PASSWORD",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465,
    "receiver_emails": [
        "reciver1@example.de",
        "reciver2@example.de"
    ],
    "message_users_fremdschluessel": "1000",
    "message_rics": "",
    "status_dict": {
    }
}

## Der Cronjob zum starten könnte so aussehen (contab -e):
Alle 5 Min prüfen ob sich ein Fahrzeug Status geändert hat
*/5 * * * * /usr/bin/python3 /home/pi/Divera_FMS/main.py >> /home/pi/Divera_FMS/log.txt 2>&1
