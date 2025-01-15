import pandas as pd
from datetime import datetime
from collections import defaultdict

fichier = "../csv/reporting_web_session_gmv.csv"
fichier2 = "../csv/tracking_ecom_events.csv"

# dq per country per month

def load_file(f):
    try:
        df_load = pd.read_csv(f, sep=",")
        df_load['date_day'] = pd.to_datetime(df_load['date_day']).dt.strftime('%d/%m/%Y')
        if (df_load.empty):
            print("le fichier est vide")
            return None
        else:
            print("le fichier est bien chargé")
            return df_load
    except ValueError:
        print("erreur lors du chargement du fichier")

def load_file_track(f):
    try:
        df_load = pd.read_csv(f, sep=",", usecols=["session_id", "country_code", "date"])
        if (df_load.empty):
            print("le fichier est vide")
            return None
        else:
            print("le fichier est bien chargé")
            return df_load
    except ValueError:
        print("erreur lors du chargement du fichier")

## On réfléchit en terme de lignes
## créer un dictionnaire par soucis de vitesse


def completeness_per_country(df):
    # Dictionnaire pour suivre les valeurs par (country, year, month)
    completeness_results = defaultdict(lambda: {"missing": 0, "N_case": 0})

    # Parcourir chaque ligne du DataFrame
    for i in range(len(df)):
        row = df.iloc[i]
        cc = row["country_code"]
        if pd.isna(cc): 
            continue

        date = row["date_day"]
        date_obj = datetime.strptime(date, "%d/%m/%Y") 
        year, month = date_obj.year, date_obj.month

        # Calculer les valeurs manquantes et totales pour la ligne
        missing_case = row.isnull().sum()
        N_case_per_row = row.count() + missing_case

        # Ajouter les valeurs à la clé (country, year, month)
        completeness_results[(cc, month, year)]["missing"] += missing_case
        completeness_results[(cc, month, year)]["N_case"] += N_case_per_row

    # Calculer les pourcentages de complétude pour chaque clé
    for key, values in completeness_results.items():
        missing = values["missing"]
        N_case_tot = values["N_case"]
        completeness_percentage = ((N_case_tot - missing) / N_case_tot) * 100
        completeness_results[key]["completeness_percentage"] = completeness_percentage

    return completeness_results


def uniqueness_per_country(df):
    # Assurer que "date_day" est de type datetime
    df["date_day"] = pd.to_datetime(df["date_day"], format="%d/%m/%Y")


    # Extraire les combinaisons uniques de pays, années et mois
    unique_combinations = df[["country_code", "date_day"]].dropna()
    unique_combinations["year"] = unique_combinations["date_day"].dt.year
    unique_combinations["month"] = unique_combinations["date_day"].dt.month
    unique_combinations = unique_combinations[["country_code", "year", "month"]].drop_duplicates()

    # Dictionnaire pour stocker les résultats
    uniqueness_result = {}

    # Parcourir chaque combinaison (pays, année, mois)
    for _, row in unique_combinations.iterrows():
        cc = row["country_code"]
        year = row["year"]
        month = row["month"]

        row_per_country = df[
            (df["country_code"] == cc) &
            (df["date_day"].dt.year == year) &
            (df["date_day"].dt.month == month)
        ]

        N_doublon = row_per_country.duplicated().sum()
        uniqueness_percent = 100 - ((N_doublon / len(row_per_country)) * 100)

        uniqueness_result[(cc, month, year)] = {
            "uniqueness_percentage": uniqueness_percent,
            "N_doublons": N_doublon,
            "total_records": len(row_per_country)
        }

    return uniqueness_result






def check_value(value):
    unique_dates = set()
    if pd.isnull(value): 
        return unique_dates
    try:
        unique_dates.add(value.strftime("%d/%m/%Y"))
    except ValueError:
        pass 
    return unique_dates



def timeliness_per_country(df):
    dates_by_month_per_country = defaultdict(set)
    timeliness_result = {}   
    for i in range(len(df)):
        value = df["date_day"][i]
        cc = df["country_code"][i]
        valid_dates = check_value(value)
        for date in valid_dates:
            date_obj = datetime.strptime(date, "%d/%m/%Y")
            dates_by_month_per_country[(cc, date_obj.year, date_obj.month)].add(date_obj.day)
    for (cc, year, month), days in sorted(dates_by_month_per_country.items()):
        if month in [4, 6, 9, 11]: 
            N_days = 30
        elif month == 2:  
            N_days = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
        else: 
            N_days = 31

        percent = (len(days) / N_days) * 100
        timeliness_result[(cc, month, year)] = {"timeliness_percentage": percent}
        # print(f"Pays : {cc}, Année : {year}, Mois : {month}, Jours où les données sont remplies: {len(days)}/{N_days}")
        # print(f"Pourcentage de jour où les données ont été remplies pour le mois: {percent:.2f}%\n")
    return timeliness_result


def count_sessions_tracking_per_country(df, session_column, cc):
    print("yo: ", df[(df["country_code"] == cc)])
    N_session_t_tot = len(df[(df["country_code"] == cc) & df[session_column].notnull()])
    print(f"session total pour le tracking : {N_session_t_tot}")
    return N_session_t_tot

def count_sessions_reporting_per_country(df, session_column, cc):
    N_session_r_tot = df[df["country_code"] == cc][session_column].sum()
    print(f"session total pour le reporting : {N_session_r_tot}")
    return N_session_r_tot


def period_filter(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column])
    print("date:", df[date_column].head())
    filtered_date = df[(df[date_column] >= datetime(2024,9,1)) & (df[date_column] <= datetime(2024,12,1))]
    return filtered_date


def integrity_per_country(f1,f2):
    df1 = load_file(f1)
    df2 = load_file_track(f2)
    unique_countries_code = df1["country_code"].unique()
    unique_countries_code2 = df2["country_code"].unique()
    print("1", unique_countries_code)
    print("2", unique_countries_code2)
    filtered_df1 = period_filter(df1, "date_day")
    filtered_df2 = period_filter(df2, "date")
    for cc in unique_countries_code:
        session_tot_r = count_sessions_reporting_per_country(filtered_df1, "number_of_sessions",cc)
        session_tot_t = count_sessions_tracking_per_country(filtered_df2, "session_id", cc)
        if session_tot_r + session_tot_t > 0:
            percent_gap = (abs(session_tot_r - session_tot_t) / ((session_tot_r + session_tot_t) / 2)) * 100
            print(f"le pourcentage d'écart pour le pays {cc} est de {percent_gap:.2f}%")

        else:
            print(f"Aucune session enregistrée pour le pays {cc}.")
    
def result():
    df = load_file(fichier)
    print("resultat")
    completeness_per_country_r = completeness_per_country(df)
    uniqueness_per_country_r = uniqueness_per_country(df)
    timeliness_per_country_r = timeliness_per_country(df)
    results_data = []
    for country, values in completeness_per_country_r.items():
        results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "completeness",
            "country": country[0],
            "percentage": values["completeness_percentage"],
            "month": country[1],
            "year": country[2],
            "description": "Taux de complétude des données"
        })

    # Ajouter les résultats d'unicité
    for country, values in uniqueness_per_country_r.items():
        results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "uniqueness",
            "country": country[0],
            "month": country[1],
            "year": country[2],
            "percentage": values["uniqueness_percentage"],
            "description": "Taux d'unicité des données"
        })
    # Ajouter les résultats de timeliness
    print(timeliness_per_country_r)
    for country, values in timeliness_per_country_r.items():
        print("valeurs ",values)
        results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "timeliness",
            "country": country[0],
            "percentage": values["timeliness_percentage"],
            "month": country[1],
            "year": country[2],
            "description": "Taux d'actualité des données"
        })

    results_df = pd.DataFrame(results_data)
    df_sorted = results_df.sort_values(by=["result_type", "country", "year", "month"])

        # Exporter vers un fichier Excel
    df_sorted.to_excel("resultats_par_pays.xlsx", index=False)
    print("Fichier Excel créé : resultats_par_pays.xlsx")

def menu():
    df = load_file(fichier)
    switch = {
        1: lambda: completeness_per_country(df),
        2: lambda: uniqueness_per_country(df),
        3: lambda: timeliness_per_country(df),
        4: lambda: integrity_per_country(fichier, fichier2),

    }
    try:
        choix = int(input("complétude tapez 1,\n unicité tapez 2,\n timeliness tapez 3\n, intégrité tapez 4\n"))
    except ValueError:
        print("erreur lors de la saisie du nombre")
        return
    action = switch.get(choix, lambda: print("Option invalide."))
    action() 
