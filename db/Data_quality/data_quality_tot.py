import pandas as pd
from datetime import datetime
from collections import defaultdict

fichier = '../csv/reporting_web_session_gmv_v2.csv'
fichier2 = '../csv/tracking_ecom_events.csv'

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
    
def load_file_track(f):
    try:
        df_load = pd.read_csv(f, sep=",", usecols=["session_id", "date"])
        unique_dates = df_load["date"].dropna().unique()
        unique_dates = sorted(unique_dates) 
        if (df_load.empty):
            print("le fichier est vide")
            return None
        else:
            print("le fichier est bien chargé")
            return df_load
    except ValueError:
        print("erreur lors du chargement du 2ème fichier")
    
## Complétude des données totale
def completeness(df): 
    total_cells = df.size
    total_missing = df.isnull().sum().sum()
    percent_completeness = (1 - (total_missing / total_cells)) * 100
    print(f"Le pourcentage de complétude totale pour la table vaut {percent_completeness:.2f}%")
    completeness_result = {"completeness_percentage": percent_completeness}
    return completeness_result

    
def uniqueness(df):
    N_doublon = df.duplicated().sum()
    N_lignes = len(df)
    percent_doublon = (N_doublon / N_lignes) * 100
    uniqueness_result = {"uniqueness_percentage" :percent_doublon}
    print(f"Le pourcentage de doublon pour la table vaut {percent_doublon:.2f}%")
    return uniqueness_result


def check_value(value):
    unique_dates = set()
    if pd.isnull(value): 
        return unique_dates
    try:
        value = str(value)
        date = datetime.strptime(value, "%d/%m/%Y")
        unique_dates.add(date.strftime("%d/%m/%Y"))
    except ValueError:
        pass 
    return unique_dates

def timeliness(df):
    dates_by_month = defaultdict(set)
    for value in df["date_day"]:
        valid_dates = check_value(value)
        for date in valid_dates:
            date = datetime.strptime(date, "%d/%m/%Y")
            dates_by_month[(date.year, date.month)].add(date.day)
    timeliness_percentages = []
    for (year, month), days in sorted(dates_by_month.items()):
        if month in [4, 6, 9, 11]:
            N_days = 30
        elif month == 2:
            N_days = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
        else:
            N_days = 31
        percent = (len(days) / N_days) * 100
        timeliness_percentages.append(percent)
    timeliness_tot = (100 - (sum(timeliness_percentages) / len(timeliness_percentages))) if timeliness_percentages else 0
    timeliness_result = {"timeliness_percentage": timeliness_tot}
    print(f"Le pourcentage de jour où les données n'ont pas été inscrites pour la table vaut {timeliness_tot:.2f}%")
    
    return timeliness_result



def period_filter(df, date_column):
    filtered_date = df[(df[date_column] >= datetime(2024,9,1)) & (df[date_column] <= datetime(2024,12,1))]
    return filtered_date



# intégrité des donées sur la période de septembre 2024 à décembre 2024
def integrity_df(f1,f2):
    df1 = pd.read_csv(f1, sep=',', usecols=["date_day", "number_of_sessions", "country_code"])
    df1= df1[df1["country_code"] == "FR"]
    df1 = df1.groupby("date_day", as_index=False)["number_of_sessions"].sum()

    df2 = load_file_track(f2)
    df1["date_day"] = pd.to_datetime(df1["date_day"], format="%d/%m/%Y", errors='coerce')
    df2["date"] = pd.to_datetime(df2["date"])
    df2_summed = df2.groupby('date')['session_id'].size().reset_index(name='sessions_count')
    result = df1.merge(df2_summed, left_on='date_day', right_on='date', how='left')
    result = result.drop("date", axis=1)
    return result

def integrity(df_merge, date_column):
    print("intégrité pour le pays FR")
    df_filtered = period_filter(df_merge, date_column)
    integrity_per_m = defaultdict(dict)

    for _, row in df_filtered.iterrows():
        year = row[date_column].year
        month = row[date_column].month
        if not pd.isna(row["sessions_count"]) and not pd.isna(row["number_of_sessions"]):
            # Calculer la différence entre session_count et session_sum pour chaque ligne
            session_diff = abs(row["sessions_count"] - row["number_of_sessions"])
            if (month, year) not in integrity_per_m:
                integrity_per_m[(month, year)] = {"session_diff": 0}

            integrity_per_m[(month, year)]["session_diff"] += session_diff


    # Afficher les résultats
    print("pourcentage d'écart entre le reporting et le tracking & Résultats d'intégrité mensuelle :")

    return integrity_per_m

# integrity(integrity_df(fichier,fichier2), "date_day")
            




def result():
    df = load_file(fichier)
    completeness_per_country_r = completeness(df)
    uniqueness_per_country_r = uniqueness(df)
    timeliness_per_country_r = timeliness(df)
    integrity__per_country_r = integrity(integrity_df(fichier,fichier2), "date_day")
    results_data = []
    results_data.append({
        "nom_de_la_table": "reporting",
        "result_type": "completeness",
        "percentage": completeness_per_country_r["completeness_percentage"],
        "description": "Taux de complétude des données"
    })
    results_data.append({
        "nom_de_la_table": "reporting",
        "result_type": "uniqueness",
        "percentage": uniqueness_per_country_r["uniqueness_percentage"],
        "description": "Taux d'unicité des données"
    })
    results_data.append({
            "nom_de_la_table": "reporting",
            "result_type": "timeliness",
            "percentage": timeliness_per_country_r["timeliness_percentage"],
            "description": "Taux de ponctualité des données"
    })
    for key, values in integrity__per_country_r.items():
        results_data.append({
            "nom_de_la_table": "écart reporting tracking",
            "result_type": "integrity",
            "gap": values["session_diff"],
            "description": "intégrité des données (écart)"
        })

    results_df = pd.DataFrame(results_data)

        # Exporter vers un fichier Excel
    results_df.to_excel("resultats_tot.xlsx", index=False)

    print("Fichier Excel créé : resultats_tot.xlsx")

# result()
def menu():
    df = load_file(fichier)
    switch = {
        1: lambda: completeness(df),
        2: lambda: uniqueness(df),
        3: lambda: timeliness(df),
        4: lambda: integrity(integrity_df(fichier,fichier2), "date_day"),
    }
    try:
        choix = int(input("complétude tapez 1,\n unicité tapez 2,\n timeliness tapez 3\n, intégrité tapez 4\n"))
    except ValueError:
        print("erreur lors de la saisie du nombre")
        return
    action = switch.get(choix, lambda: print("Option invalide."))
    action() 

    # ajouter une colonne sur les mois pour filtrer