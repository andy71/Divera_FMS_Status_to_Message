import urllib.request
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from datetime import datetime

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
        print("    \"sender_email\": \"sender@example.de\",")
        print("    \"email_password\": \"YOUR-EMAIL-PASSWORD\",")
        print("    \"smtp_server\": \"smtp.gmail.com\",")
        print("    \"smtp_port\": 465,")
        print("    \"receiver_emails\": [")
        print("        \"reciver1@example.de\",")
        print("        \"reciver2@example.de\"")
        print("    ],")
        print("    \"message_users_fremdschluessel\": \"1000,1001\",")
        print("    \"message_rics\": \"22,23\",")
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

def send_email(content, sender_email, receiver_emails, password, smtp_server, smtp_port):
    # E-Mail Inhalt erstellen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = "Änderung Fahrzeugstatus!"

    body = content
    msg.attach(MIMEText(body, 'plain'))

    # E-Mail Server einrichten und verbinden
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.ehlo()
        server.login(sender_email, password)

        # E-Mail senden
        text = msg.as_string()
        server.sendmail(sender_email, receiver_emails, text)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | E-Mail erfolgreich gesendet!")
    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Fehler: Authentifizierung fehlgeschlagen. Stelle sicher, dass Benutzername und Passwort korrekt sind.")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Details:", auth_error)
    except smtplib.SMTPException as smtp_error:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Fehler beim Senden der E-Mail.")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Details:", smtp_error)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Ein allgemeiner Fehler ist aufgetreten:", e)
    finally:
        if 'server' in locals():
            server.quit()

def send_push(message_titel, message_text, api_key, message_users_fremdschluessel, message_rics):
    if message_users_fremdschluessel != "":
        message_url = f"https://app.divera247.com/api/news?title={urllib.parse.quote(message_titel)}&text={urllib.parse.quote(message_text)}&person={message_users_fremdschluessel}&accesskey={api_key}"
        urllib.request.urlopen(message_url)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Mitteilung erfolgreich versendet.")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Keine Divera User angegeben. Mitteilung wird nicht versendet.")
    if message_rics != "":
        message_url = f"https://app.divera247.com/api/news?title={urllib.parse.quote(message_titel)}&text={urllib.parse.quote(message_text)}&ric={message_rics}&accesskey={api_key}"
        urllib.request.urlopen(message_url)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Mitteilung erfolgreich versendet.")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Keine Divera Rics angegeben. Mitteilung wird nicht versendet.")

def main():
    config = load_config()
    api_key = config["api_key"]
    message_users_fremdschluessel = config["message_users_fremdschluessel"]
    message_rics = config["message_rics"]
    sender_email = config["sender_email"]
    receiver_emails = config["receiver_emails"]
    password = config["email_password"]
    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    message_titel = "Änderung Fahrzeugstatus!"
    url = f"https://app.divera247.com/api/v2/pull/vehicle-status?accesskey={api_key}"

    # Status jeder ID speichern
    status_dict = config.get("status_dict", {})

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            for item in data["data"]:
                id = str(item["id"])  # ID als Zeichenkette speichern
                fullname = item["fullname"]
                shortname = item["shortname"]
                fmsstatus = item["fmsstatus"]

                # Wenn die ID noch nicht im status_dict ist, füge sie hinzu
                if id not in status_dict:
                    status_dict[id] = fmsstatus
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ID wurde hinzugefügt. Aktueller status_dict:", status_dict)
                else:
                    # Wenn sich der Status von 6 auf != 6 oder von !=6 auf 6 ändert, sende eine E-Mail und aktualisiere den Status
                    if (status_dict[id] == 6 and fmsstatus != 6) or (status_dict[id] != 6 and fmsstatus == 6):
                        if status_dict[id] == 6:
                            message = f"Ein Fahrzeug ({shortname}) ist jetzt wieder einsatzbereit. \nID: {id},\n Fahrzeugname: {fullname},\n Kurzname: {shortname},\n FMS Status: {fmsstatus}\n"
                        else:
                            message = f"Ein Fahrzeug ({shortname}) ist aktuell nicht einsatzbereit. \nID: {id},\n Fahrzeugname: {fullname},\n Kurzname: {shortname},\n FMS Status: {fmsstatus}\n"

                        # E-Mail senden
                        if receiver_emails:
                            # E-Mail senden
                            send_email(message, sender_email, receiver_emails, password, smtp_server, smtp_port)
                        else:
                            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Keine Empfänger-E-Mail-Adressen angegeben. E-Mail wird nicht versendet.")
                        # Pushnachricht senden
                        send_push(message_titel, message, api_key,message_users_fremdschluessel,message_rics)
                    # Aktualisiere den Status für die ID
                    status_dict[id] = fmsstatus

        # Speichere den Status in der Konfigurationsdatei
        config["status_dict"] = status_dict
        save_config(config)

    except Exception as e:
        print(f"Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Fehler beim Abrufen der Daten oder beim Senden der E-Mail:", e)

if __name__ == "__main__":
    main()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Script erfolgreich ausgeführt!")