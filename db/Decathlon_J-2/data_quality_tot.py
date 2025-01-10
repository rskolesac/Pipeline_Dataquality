import pandas as pd
from datetime import datetime
from collections import defaultdict

fichier = '../csv/reporting_web_session_gmv.csv'
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
        if (df_load.empty):
            print("le fichier est vide")
            return None
        else:
            print("le fichier est bien chargé")
            return df_load
    except ValueError:
        print("erreur lors du chargement du fichier")
    
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
    df[date_column] = pd.to_datetime(df[date_column])
    print("date:", df[date_column].head())
    filtered_date = df[(df[date_column] >= datetime(2024,9,1)) & (df[date_column] <= datetime(2024,12,1))]
    return filtered_date

def count_sessions_tracking(df, session_column):
    N_session_missing = df[session_column].isnull().sum()
    N_session_t_tot = len(df) - N_session_missing
    print(f"session total pour le tracking : {N_session_t_tot}")
    return N_session_t_tot

def count_sessions_reporting(df, session_column):
    N_session_r_tot = df[session_column].sum()
    print(f"session total pour le reporting : {N_session_r_tot}")
    return N_session_r_tot

def integrity(f1,f2):
    df1 = load_file(f1)
    df2 = load_file_track(f2)
    filtered_df1 = period_filter(df1, "date_day")
    filtered_df2 = period_filter(df2, "date")
    session_tot_r = count_sessions_reporting(filtered_df1, "number_of_sessions")
    session_tot_t = count_sessions_tracking(filtered_df2, "session_id")

    percent_gap =  (abs(session_tot_r - session_tot_t) / ((session_tot_r + session_tot_t) / 2)) * 100
    print(f"le pourcentage d'écart entre le nombre de session entre le tracking et le reporting vaut {percent_gap}")


def result():
    df = load_file(fichier)
    completeness_per_country_r = completeness(df)
    uniqueness_per_country_r = uniqueness(df)
    timeliness_per_country_r = timeliness(df)
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
        4: lambda: integrity(df),
    }
    try:
        choix = int(input("complétude tapez 1,\n unicité tapez 2,\n timeliness tapez 3\n, intégrité tapez 4\n"))
    except ValueError:
        print("erreur lors de la saisie du nombre")
        return
    action = switch.get(choix, lambda: print("Option invalide."))
    action() 
