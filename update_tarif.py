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
import pandas as pd
from io import StringIO
import sys

# Variables
configfile = "config.ini"


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

def get_tarif_tempo(url:str)->dict:
    tarif = {}
    # Récupère le CSV
    response = requests.get(url)
    # Si OK
    if response.status_code == 200:
        # Lire le contenu de la réponse dans un DataFrame
        df = pd.read_csv(StringIO(response.text), sep=';')

        # Recupère tarif actuel
        actuel = df[df['DATE_FIN'].isnull()]
        

    else:
        print(f"Erreur lors de la requête : {response.status_code}")
        

def main()->None:
    conf = config_read(configfile)
    tempo = get_tarif_tempo(conf['data']['tempo'])

# Main
if __name__ == "__main__":
    main()
    