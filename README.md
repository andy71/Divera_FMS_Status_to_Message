# Divera FMS Status Änderungen via Divera 24/7 Mitteilung.

Dieses Script ist eine Vereinfachung des Repos [Sleepwalker86/Divera_FMS_Status_to_Email](https://github.com/Sleepwalker86/Divera_FMS_Status_to_Email).

Dieser Fork sendet nur eine Divera Mitteilung an eine Liste von Benutzer Fremdschlüsseln wann immer sich der Fahrzeugstatus ändert.

Kopiert die config-example.json zu config.json und passt die Beispiel Parameter an.

Beispiel Config:

```json
{
    "_comment": "Diese Datei bitte kopieren und entsprechend anpassen bzw. ausfüllen. STATUS_DICT nicht ändern. Anschließend die datei in config.json umbenennen!",
    "api_key": "YOUR-API-KEY",
    "message_users_fremdschluessel": "1000,1001",
    "status_dict": {}
}
```


# Der Cronjob zum Starten könnte so aussehen (contab -e):

```crontab
# Alle 5 Min prüfen ob sich ein Fahrzeug Status geändert hat
*/5 * * * * /usr/bin/python3 /home/pi/Divera_FMS/main.py >> /home/pi/Divera_FMS/log.txt 2>&1
```

# Credits:
Thank you to:
- Sleepwalker86
