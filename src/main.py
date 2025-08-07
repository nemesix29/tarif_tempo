#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# MCBot 
#
# Authors: n3m3s1x
# Updated: 05/02/2025
# -----------------------------------------------------------------------------

# Imports
import configparser
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
from io import StringIO
import sys

# Variables
configfile = "config/config.ini"

# Fonctions
def config_read(file:str)->dict:
    config = configparser.ConfigParser()
    try:
        config.read(file)
    except:
        print(f"Impossible d'ouvrir le fichier de config : {file}")
        sys.exit(3)
    else:
        config_dict = {}
        # Parcourir chaque section
        for section in config.sections():
            config_dict[section] = {}
            # Parcourir chaque clé dans la section
            for key in config[section]:
                config_dict[section][key] = config.get(section, key)
        return config_dict

def get_tarif_tempo(url:str,out_file:str="tarif_tempo.json")->dict:
    tarif = {}
    # Récupère le CSV
    response = requests.get(url)
    # Si OK
    if response.status_code == 200:
        # Lire le contenu de la réponse dans un DataFrame
        data = pd.read_csv(StringIO(response.text), sep=';')
        # Convertir les colonnes de date en type datetime
        data['DATE_DEBUT'] = pd.to_datetime(data['DATE_DEBUT'], format='%d/%m/%Y')
        data['DATE_FIN'] = pd.to_datetime(data['DATE_FIN'], format='%d/%m/%Y')
        
        # Filtrer les données pour la date d'aujourd'hui
        today = datetime.today()
        today_data = data[(data['DATE_DEBUT'] <= today) & (data['DATE_FIN'] >= today)]
        
        # Si aucune donnée n'est trouvée pour aujourd'hui, utiliser la dernière période disponible
        if today_data.empty:
            last_start_date = data['DATE_DEBUT'].max()
            today_data = data[data['DATE_DEBUT'] == last_start_date]
        # Convertir les valeurs en float
        today_data = today_data.apply(lambda x: x.str.replace(',', '.').astype(float) if x.dtype == "object" else x)

        # Diviser les valeurs de PART_FIXE_TTC par 12 pour obtenir un prix mensuel
        today_data['PART_FIXE_TTC'] = np.ceil(today_data['PART_FIXE_TTC'] / 12 * 100) / 100
        # Préparer les données au format souhaité
        abo_kva = today_data.set_index('P_SOUSCRITE')['PART_FIXE_TTC'].to_dict()
        hp = {
            "bleu": today_data['PART_VARIABLE_HPBleu_TTC'].iloc[0],
            "blanc": today_data['PART_VARIABLE_HPBlanc_TTC'].iloc[0],
            "rouge": today_data['PART_VARIABLE_HPRouge_TTC'].iloc[0]
        }
        hc = {
            "bleu": today_data['PART_VARIABLE_HCBleu_TTC'].iloc[0],
            "blanc": today_data['PART_VARIABLE_HCBlanc_TTC'].iloc[0],
            "rouge": today_data['PART_VARIABLE_HCRouge_TTC'].iloc[0]
        }

        tarif = {
            "abo_kva": abo_kva,
            "hp": hp,
            "hc": hc
        }
        # Retour des données vers un fichier en JSON
        with open(out_file, 'w') as json_file:
            json.dump(tarif, json_file, indent=4)
        
        return tarif
    
    else:
        print(f"Erreur lors de la requête : {response.status_code}")

def get_tarif_bleu(url:str,out_file:str="tarif_bleu.json")->dict:
    tarif = {}
    # Récupère le CSV
    response = requests.get(url)
    # Si OK
    if response.status_code == 200:
        # Lire le contenu de la réponse dans un DataFrame
        data = pd.read_csv(StringIO(response.text), sep=';')
        # Convertir les colonnes de date en type datetime
        data['DATE_DEBUT'] = pd.to_datetime(data['DATE_DEBUT'], format='%d/%m/%Y')
        data['DATE_FIN'] = pd.to_datetime(data['DATE_FIN'], format='%d/%m/%Y')
        
        # Filtrer les données pour la date d'aujourd'hui
        today = datetime.today()
        today_data = data[(data['DATE_DEBUT'] <= today) & (data['DATE_FIN'] >= today)]
        
        # Si aucune donnée n'est trouvée pour aujourd'hui, utiliser la dernière période disponible
        if today_data.empty:
            last_start_date = data['DATE_DEBUT'].max()
            today_data = data[data['DATE_DEBUT'] == last_start_date]
        # Convertir les valeurs en float
        today_data = today_data.apply(lambda x: x.str.replace(',', '.').astype(float) if x.dtype == "object" else x)

        # Diviser les valeurs de PART_FIXE_TTC par 12 pour obtenir un prix mensuel
        today_data['PART_FIXE_TTC'] = np.ceil(today_data['PART_FIXE_TTC'] / 12 * 100) / 100
        # Préparer les données au format souhaité
        abo_kva = today_data.set_index('P_SOUSCRITE')['PART_FIXE_TTC'].to_dict()
        hp = today_data['PART_VARIABLE_HP_TTC'].iloc[0],
        hc = today_data['PART_VARIABLE_HC_TTC'].iloc[0],
        tarif = {
            "abo_kva": abo_kva,
            "hp": hp,
            "hc": hc
        }
        # Retour des données vers un fichier en JSON
        with open(out_file, 'w') as json_file:
            json.dump(tarif, json_file, indent=4)
        
        return tarif
    
    else:
        print(f"Erreur lors de la requête : {response.status_code}")


def main()->None:
    conf = config_read(configfile)
    tempo = get_tarif_tempo(conf['data']['tempo'])
    bleu = get_tarif_bleu(conf['data']['hchp'])
    

# Main
if __name__ == "__main__":
    main()
    