import urllib.request
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def send_email(content, sender_email, receiver_emails, password):
    # E-Mail Inhalt erstellen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = "Änderung Fahrzeugstatus"

    body = content
    msg.attach(MIMEText(body, 'plain'))

    # E-Mail Server einrichten und verbinden
    try:
        server = smtplib.SMTP_SSL('smtp.ionos.de', 465)
        server.ehlo()
        server.login(sender_email, password)

        # E-Mail senden
        text = msg.as_string()
        server.sendmail(sender_email, receiver_emails, text)
        print("E-Mail erfolgreich gesendet!")
    except smtplib.SMTPAuthenticationError as auth_error:
        print("Fehler: Authentifizierung fehlgeschlagen. Stelle sicher, dass Benutzername und Passwort korrekt sind.")
        print("Details:", auth_error)
    except smtplib.SMTPException as smtp_error:
        print("Fehler beim Senden der E-Mail.")
        print("Details:", smtp_error)
    except Exception as e:
        print("Ein allgemeiner Fehler ist aufgetreten:", e)
    finally:
        if 'server' in locals():
            server.quit()

def main():
    config = load_config()
    api_key = config["api_key"]
    sender_email = config["sender_email"]
    receiver_emails = config["receiver_emails"]
    password = config["email_password"]

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
                    print("ID wurde hinzugefügt. Aktueller status_dict:", status_dict)
                else:
                    # Wenn sich der Status von 6 auf 2 oder von 2 auf 6 ändert, sende eine E-Mail und aktualisiere den Status
                    if (status_dict[id] == 6 and fmsstatus == 2) or (status_dict[id] == 2 and fmsstatus == 6):
                        if status_dict[id] == 6:
                            message = f"Ein Fahrzeug ({shortname}) ist jetzt wieder einsatzbereit. \nID: {id},\n Fahrzeugname: {fullname},\n Kurzname: {shortname},\n FMS Status: {fmsstatus}\n"
                        else:
                            message = f"Ein Fahrzeug ({shortname}) ist aktuell nicht Einsatzbereit. \nID: {id},\n Fahrzeugname: {fullname},\n Kurzname: {shortname},\n FMS Status: {fmsstatus}\n"
                        # E-Mail senden
                        send_email(message, sender_email, receiver_emails, password)
                    # Aktualisiere den Status für die ID
                    status_dict[id] = fmsstatus

        # Speichere den Status in der Konfigurationsdatei
        config["status_dict"] = status_dict
        save_config(config)

    except Exception as e:
        print("Fehler beim Abrufen der Daten oder beim Senden der E-Mail:", e)

if __name__ == "__main__":
    main()
