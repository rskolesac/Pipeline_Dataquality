import sys
import os
import time
import schedule
# Ajouter le répertoire Decathlon_J-2 au chemin Python
path_to_module = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Decathlon_J-2'))
sys.path.append(path_to_module)

try:
    from data_quality_tot import fichier, load_file, completeness, uniqueness, timeliness
    print("Import réussi !")
except ModuleNotFoundError as e:
    print(f"Erreur d'import : {e}")



def completeness_alert(df):
    completeness_result = completeness(df)["completeness_percentage"]
    if (completeness_result < 90):
        print("alerte complétude inférieure à 90%")
    else:
        print("Tvb, Complétude supérieure à 90%")
    return


def uniqueness_alert(df):
    uniqueness_result = uniqueness(df)["uniqueness_percentage"]
    if (uniqueness_result > 0):
        print("alerte unicité supérieure à 0%")
    else:
        print("Tvb, Unicité égale 0%")
    return

def timeliness_alert(df):
    timeliness_result = timeliness(df)["timeliness_percentage"]
    if (timeliness_result > 0):
        print("alerte temporalité supérieure à 0%")
    else:
        print("Tvb, Temporalité égale 0%")
    return




def daily(f):
    print("Execution du contrôle quotidien de qualité des données")
    df = load_file(fichier)
    completeness_alert(df)
    uniqueness_alert(df)
    timeliness_alert(df)
    schedule.every().day.at("10:00").do(daily)
    while True:
        schedule.run_pending()
        time.sleep(1)
daily(fichier)