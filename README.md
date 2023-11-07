# 3PR : Tableau de bord halterophilie France

# Infos clés
Ce projet est basé sur les données Scoresheet appartenant la FFHM.

Les données sont récupérés via un script en ruby.
Ces données sont chargées dans une base de données SQL Lite (pages\dataltero.db) via un script en Python.
Chaque page utilise des requêtes qui se sourcent sur cette base SQL Lite.
Le traitement des données de ces requêtes 
La visualisation des données est basée sur Plotly / Dash.
L'interface et la navigation se base sur Dash Bootstrap Components.

# Mise à jour
Actuellement la mise à jour est lancée manuellement avec un objectif de mise à jour hebdomadaire le dimanche soir ou lundi des semaines avec des compétitions.

# Pages
Athlètes : Permet d'analyser dans le détail toutes les compétitions d'un athlète ou de comparer des athlètes entre eux sur une période de temps.
Club : Classement par an des athlètes d'un ou plusieurs clubs / ligues
Listings : Classement par an par catégorie d'âge, de poids et par ligue
