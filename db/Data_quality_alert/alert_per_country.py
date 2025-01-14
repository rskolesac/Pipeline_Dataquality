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

# Ajouter le répertoire Decathlon_J-2 au chemin Python
path_to_module = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Data_quality'))
sys.path.append(path_to_module)

try:
    from data_quality_per_country import fichier, load_file, completeness_per_country, uniqueness_per_country, timeliness_per_country
    print("Import réussi !")
except ModuleNotFoundError as e:
    print(f"Erreur d'import : {e}")


def completeness_per_country_alert(df):
    p = []
    for country, metrics in completeness_per_country(df).items():
        if (metrics["completeness_percentage"] < 90):
            p.append(f"alerte complétude inférieure à 90% pour le pays {country[0]} au mois de {country[1]} {country[2]} (<span>{metrics["completeness_percentage"]:.2f}%</span>)\n")
    return p


def uniqueness_per_country_alert(df):
    p = []
    for (country, metrics) in uniqueness_per_country(df).items():
        if (metrics["uniqueness_percentage"] < 100):
            p.append(f"alerte unicité supérieure à 0% pour le pays {country[0]} au mois de {country[1]} {country[2]}, <span>({metrics["uniqueness_percentage"]:.2f}%</span>)\n")
    return p

def timeliness_per_country_alert(df):
    p = []
    for (country, metrics) in timeliness_per_country(df).items():
        if (metrics["timeliness_percentage"] < 100):
            p.append(f"alerte temporalité supérieure à 0% pour le pays {country[0]} au mois de {country[1]} {country[2]}, (<span>{metrics["timeliness_percentage"]:.2f}%</span>)\n")
    return p

df = load_file(fichier)
completeness = completeness_per_country_alert(df)
uniqueness = uniqueness_per_country_alert(df)
timeliness = timeliness_per_country_alert(df)

html_completeness_alerts = "".join(
    f"<li>{alert}</li>" for alert in completeness
)
html_uniqueness_alerts = "".join(
    f"<li>{alert}</li>" for alert in uniqueness
)
html_timeliness_alerts = "".join(
    f"<li>{alert}</li>" for alert in timeliness
)
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
        div {{
            padding: 10px;
        }}
        h2 {{
            color: darkblue;
            font-size: 1.2em;
        }}
        li {{
            list-style: none;
        }}
        span {{
            color: red;
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
    <p>Voici le résumé de la qualité des données par pays</p>
    <div class="result-container">
        <div class="completeness">
            <h2>Complétude : </h2>
            <ul>
                {html_completeness_alerts}
            </ul>
            <p>Aucun autre problème de complétude</p>
        </div>
        <div class="uniqueness">
            <h2>Unicité : </h2>   
            <ul> 
                {html_uniqueness_alerts}   
            </ul>    
            <p>Aucun autre problème d'unicité</p>     
        </div>
        <div class="timeliness">
            <h2>Timeliness : </h2>    
            <ul>
                {html_timeliness_alerts}
            </ul>
            <p>Aucun autre problème de timeliness</p>
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
