import sys
import os
import time
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration SMTP
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "pierrebachelet934@gmail.com"
password = "iqfr onqn ymxb wtwx"
recipient_email = "pierrebachelet934@gmail.com"

    # Créer le message
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = recipient_email
message["Subject"] = "Alerte quotidienne de la qualité des données Decathlon reporting (complétude, unicité, timeliness ,intégrité)"




path_to_module = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_quality'))
sys.path.append(path_to_module)

try:
    from data_quality_tot import fichier, fichier2, load_file, completeness, uniqueness, timeliness, integrity, integrity_df, period_filter
    print("Import réussi !")
except ModuleNotFoundError as e:
    print(f"Erreur d'import : {e}")



def completeness_alert(df):
    completeness_result = completeness(df)["completeness_percentage"]
    p = "résultat de complétude\n"
    if (completeness_result < 90):
        p += f"alerte complétude inférieure à 90%, (<span>{completeness_result:.2f}</span>)%\n"
    else:
        p += f"Tvb, Complétude supérieure à 90%\n"
    return p


def uniqueness_alert(df):
    uniqueness_result = uniqueness(df)["uniqueness_percentage"]
    p = "résultat d'unicité\n"
    if (uniqueness_result > 0):
        p += f"alerte unicité supérieure à 0% (<span>{uniqueness_result:.2f}</span>)%\n"
    else:
        p += "Tvb, Unicité égale 0%\n"
    return p

def timeliness_alert(df):
    timeliness_result = timeliness(df)["timeliness_percentage"]
    p = "résultat de timeliness\n"
    if (timeliness_result > 0):
        p += f"alerte temporalité supérieure à 0%, (<span>{timeliness_result:.2f}</span>)%\n"
    else:
        p += "Tvb, Temporalité égale 0%\n"
    return p

def integrity_alert():
    integrity_result = integrity(integrity_df(fichier, fichier2), "date_day")
    p = "résultat d'intégrité\n"
    for (key, value) in integrity_result.items():
        if (value["session_diff"] > 10000):
            p += f"alerte écart trop grand entre le reporting et le tracking, (<span>{value["session_diff"]}</span>) pour le mois de {key[0]} {key[1]}\n"
        
    p += "aucun autre problème d'intégrité\n"
    return p

df = load_file(fichier)
completeness = completeness_alert(df)
uniqueness = uniqueness_alert(df)
timeliness = timeliness_alert(df)
integrity = integrity_alert()
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .result-container {{
            display: flex;
            flex-direction: row;
        }}
        h2 {{
            color: darkblue;
            font-size: 1.2em;
        }}
        span {{
            color: red;
        }}
        div {{
            padding: 10px;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 0.9em;
            color: #666;
        }}

    </style>
</head>
<body>
    <h1>Alerte quotidienne - Qualité des données</h1>
    <p>Bonjour,</p>
    <p>Voici le résumé de la qualité des données globales</p>
    <div class="result-container">
        <div class="completeness">
            <h2>Complétude : </h2>
            <p>{completeness}</p>
        </div>
        <div class="uniqueness">
            <h2>Unicité : </h2>    
            <p>{uniqueness}</p>            
        </div>
        <div class="timeliness">
            <h2>Timeliness : </h2>    
            <p>{timeliness}</p>   
        </div>
        <div class="integrity">
            <h2>Intégrité : </h2>
            <p>{integrity}</p>
        </div>
    </div>
    <p>Merci de prendre les mesures nécessaires pour corriger les anomalies identifiées.</p>
    <div class="footer">
        <p>Cet email est généré automatiquement. Veuillez ne pas répondre directement à ce message.</p>
        <p>Contactez l'équipe Data Quality pour toute question.</p>
    </div>
</body>
</html>
"""


def mail_daily(fichier):
    print("Execution du contrôle quotidien de qualité des données")

    message.attach(MIMEText(html_content, "html"))
    # Connexion au serveur et envoi
    try:
        # Connexion au serveur
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Passage en mode sécurisé
            server.login(sender_email, password)  # Authentification
            server.sendmail(sender_email, recipient_email, message.as_string())  # Envoi
            print("Email envoyé avec succès !")
    except Exception as e:
        print(f"Erreur : {e}")



def daily(f):
    mail_daily(f)
    schedule.every().day.at("10:00").do(daily)
    while True:
        schedule.run_pending()
        time.sleep(1)
daily(fichier)