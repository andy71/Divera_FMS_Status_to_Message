# Divera FMS Status Änderungen via Divera 24/7 Mitteilung

Dieses Script ist eine Vereinfachung des Repos [Sleepwalker86/Divera_FMS_Status_to_Email](https://github.com/Sleepwalker86/Divera_FMS_Status_to_Email).

Dieser Fork sendet nur noch Divera Mitteilungen an eine Liste von Benutzern (via Fremdschlüssel) wann immer sich der Fahrzeugstatus ändert.

Darüber hinaus kann die Autoarchivierung genutzt werden um die Mitteilungen nach konfigurierbarer Zeit in das Archiv zu verschieben.

Kopiert die config-example.json zu config.json und passt die Beispiel Parameter an.

## config-example.json
```json
{
    "_comment": "Diese Datei bitte kopieren und entsprechend anpassen bzw. ausfüllen. STATUS_DICT nicht ändern. Anschließend die Datei in config.json umbenennen!",
    "api_key": "YOUR-API-KEY",
    "message_users_fremdschluessel": ["1000", "1001"],
    "autoarchive_days": 0,
    "autoarchive_hours": 0,
    "autoarchive_minutes": 0,
    "autoarchive_seconds": 0,
    "status_dict": {}
}
```
Die "autoarchive_*-Einträge ebenso wie der Eintrag "StatusLogFile" sind optional.

Die "autoarchive_*-Einträge können beliebig kombiniert und genutzt werden um die Mitteilung automatisch archivieren zu lassen.

Wenn ein StatusLogFile angegeben wird, werden darin die Statusänderungen aufgezeichnet.
Der Pfad dafür kann relativ zum Scriptpfad sein oder ein absoluter Pfad.

Statt des Eintrags "message_users_fremdschluessel" kann auch "message_groups_title" genutzt werden um eine Gruppenbezeichnung anzugeben.

```    "message_groups_title": ["Ortsbrandmeister", "Gerätewarte"],```

Es dürfen aber immer nur Gruppen oder nur Benutzer eingetragen werden, niemals beides.

# Cronjob
Der Cronjob zum Starten könnte so aussehen (contab -e):

```crontab
# Alle 5 Min prüfen ob sich ein Fahrzeug Status geändert hat
*/5 * * * * /usr/bin/python3 /home/pi/Divera_FMS/main.py >> /home/pi/Divera_FMS/log.txt 2>&1
```

# Credits:
Thank you to:
- Sleepwalker86
