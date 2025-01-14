import pandas as pd
import re

fichier = './csv/Walmart.csv'
## chargement de la db
def load_file(f):
    try: 
        df_load = pd.read_csv(f, sep=';')
        if (df_load.empty):
            print("le fichier est vide\n")
            return
        else:
            print("le fichier est bien chargé\n")
            return df_load
    except FileNotFoundError:
        print("erreur lors du chargement du fichier\n")
        return
    

def extract_date(value):
    match = re.search(r'\d{2}/\d{2}/\d{4}', value)
    match2 = re.search(r'\d{1}/\d{2}/\d{4}', value)
    if (match):
        return match.group(0)
    elif (match2):
        return match2.group(0)
    elif (value == ""):
        return ""
    else:
        return ""


def split_store_location(df):
    df[["ville","tag"]] = df["store_location"].str.split(", ", expand= True)
    df.drop(columns = "store_location")
    display_column(df)
    display_column(df)

def transaction_date_conform(df):
    ## changer les dates non remplies par des cases vides
    df["transaction_date"].fillna("")
    ## extraire les dates correctement écrites dans une nouvelle colonne
    df["cleaned_date"] = df["transaction_date"].apply(extract_date)
    ## supprimer la colonne corrompue
    df.drop(columns = "transaction_date")
    display_column(df)

def display_column(df):
    print(df.columns)
    colonne = input("Choisir une colonne à afficher : ")
    if colonne in df.columns:
        print(df[colonne]) 
    else:
        print(f"La colonne '{colonne}' n'existe pas dans le DataFrame.")


def menu():
    df = load_file(fichier)
    switch = {
        1: lambda: transaction_date_conform(df),
        2: lambda: display_column(df),
        3: lambda: split_store_location(df),
    }
    try:
        choix = int(input("pour conformer les dates tapez 1,\n pour afficher une colonne tapez 2,\n pour separer les colonnes store_location tapez 3\n"))
    except ValueError:
        print("erreur lors de la saisie du nombre")
        return
    action = switch.get(choix, lambda: print("Option invalide."))
    action() 

menu()