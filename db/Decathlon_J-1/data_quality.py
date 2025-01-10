import pandas as pd
from datetime import datetime
from collections import defaultdict

fichier = '../csv/reporting_web_session_gmv.csv'
## chargement de la db
def load_file(f):
    try: 
        df_load = pd.read_csv(f, sep=',')
        if (df_load.empty):
            print("le fichier est vide\n")
            return
        else:
            print("le fichier est bien chargé\n")
            return df_load
    except FileNotFoundError:
        print("erreur lors du chargement du fichier\n")
        return
    
## Complétude des données (par colonne)
def completeness(df): 
    completeness_result= {}
    for column in df.columns:
        N_case = len(df[column])
        N_case_empty = df[column].isnull().sum()
        percent_completeness = (1 - (N_case_empty / N_case)) * 100
        completeness_result[column] = {"completeness_percentage": percent_completeness}
        print(f"Le pourcentage de complétude pour la colonne '{column}' vaut {percent_completeness:.2f}%")
    return completeness_result
    
def uniqueness(df):
    N_doublon = df.duplicated().sum()
    N_lignes = len(df)
    percent_doublon = (N_doublon / N_lignes) * 100
    uniqueness_result = percent_doublon
    print(f"Le pourcentage de doublon pour la table vaut {percent_doublon:.2f}%")
    return uniqueness_result



def check_value(value):
    unique_dates = set()
    try:
        date = datetime.strptime(value, "%d/%m/%Y")
        unique_dates.add(date.strftime("%d/%m/%Y"))
    except ValueError:
        print("Date invalide")

    return unique_dates



def timeliness(df):
    dates_by_month = defaultdict(set)
    timeliness_result = {}
    for value in df["date_day"]:
        valid_dates = check_value(value)
        for date in valid_dates:
            date = datetime.strptime(date, "%d/%m/%Y")
            dates_by_month[(date.year, date.month)].add(date.day)

    for (year, month), days in sorted(dates_by_month.items()):
        N_days = 31
        if (month in [4,6,9,11]):
            N_days = 30
        elif (month == 2):
            N_days = 28
        percent = (len(days) / N_days) * 100
        timeliness_result[month] = {"timeliness_percentage": percent}
        print(N_days, (year,month), days)
        print(f"le pourcentage de jour où les données ont été inscrites en {month, year} vaut {percent}%")
    return timeliness_result




def result():
    df = load_file(fichier)
    completeness_per_country_r = completeness(df)
    uniqueness_per_country_r = uniqueness(df)
    timeliness_per_country_r = timeliness(df)
    results_data = []
    for key, values in completeness_per_country_r.items():
        results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "completeness",
            "percentage": values["completeness_percentage"],
            "commentaire": "Taux de complétude des données"
        })
        results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "uniqueness",
            "percentage": uniqueness_per_country_r,
            "commentaire": "Taux d'unicité des données"
        })
    # Ajouter les résultats de timeliness
    for key, values in timeliness_per_country_r.items():
        print(values)
        results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "timeliness",
            "percentage": values["timeliness_percentage"],
            "commentaire": "Taux de ponctualité des données"
        })

    results_df = pd.DataFrame(results_data)

        # Exporter vers un fichier Excel
    results_df.to_excel("resultats_tot.xlsx", index=False)

    print("Fichier Excel créé : resultats_par_pays.xlsx")




def menu():
    df = load_file(fichier)
    switch = {
        1: lambda: completeness(df),
        2: lambda: uniqueness(df),
        3: lambda: timeliness(df),
    }
    try:
        choix = int(input("complétude tapez 1,\n unicité tapez 2,\n timeliness tapez 3\n"))
    except ValueError:
        print("erreur lors de la saisie du nombre")
        return
    action = switch.get(choix, lambda: print("Option invalide."))
    action() 

menu()