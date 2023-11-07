import dash
import plotly.express as px
from dash import dash_table, dcc, html, callback
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
import numpy as np
import os
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from flask import Flask, render_template

# Connection à la base SQLite
dirname = os.path.dirname(__file__)
path_db = os.path.join(dirname, 'dataltero.db')
conn = sql.connect(database=path_db)

# Requête TODO : associer les max IWF à une compétition précise (lieu, date...) dans la BDD
qry = """SELECT * FROM
            (SELECT distinct
                ath.Nom                     as "Nom"
            ,   ath.DateNaissance           as "Né le"
            ,   ath."Nationalite"           as "Pays"
            ,   clb.Club                    as "Club"
            ,   clb.Ligue                   as "Ligue"
            ,   cat."Sexe"                  as "Sexe"
            ,   cat."Serie"                 as "Serie"
            ,   cat."CatePoids"             as "CatePoids"
            ,   cat."CateAge"               as "CateAge"
            ,   cat."Serie"                 as "Série"
            ,   cat.Arrache                 as "Arr"
            ,   cat.EpJete                  as "EpJ"
            ,   cat.PoidsTotal              as "Total"
            ,   cat.PoidsDeCorps            as "PdC"
            ,   cat.IWF_Calcul              as "IWF"
            ,   cmp.NomCompetitionCourt     as "Compet"
            ,   cmp.DateCompet              as "Date"
            ,   apr.SaisonAnnee             as "SaisonAnnee"
            ,   apr.MaxIWFSaison            as "Max IWF Saison"
            ,   apr.MaxIWF                  as "Max IWF"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee", cat.CatePoids
                                  order by cat.IWF_Calcul desc) as "RowNum"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee"
                                  order by cat.IWF_Calcul desc) as "RowNumMaxSaison"
          FROM ATHLETE as ath 
          LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
          LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
          LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
          LEFT JOIN ATHLETE_PR as apr on apr.AthleteID = ath.AthleteID and apr.SaisonAnnee = cmp.SaisonAnnee)
      WHERE RowNum=1"""

df = pd.read_sql_query(qry, conn)
df.head()

# Arrondi à 3 virgule pour l'IWF pour le display
df['Max IWF Saison'] = round(df['Max IWF Saison'], 3)
df['Max IWF'] = round(df['Max IWF'], 3)
df['IWF'] = round(df['IWF'], 3)

updated_title = 'Listings'

# app = dash.Dash(__name__)
dash.register_page(__name__)
# server = server


# df_unique_names = df['Nom'].unique  # Fetch or generate data from Python
nom_ligue = list(set(df['Ligue'].tolist()))
nom_age = list(set(df['CateAge'].tolist()))
nom_poids = list(set(df['CatePoids'].tolist()))
nom_sexe = list(set(df['Sexe'].tolist()))

# body
layout = html.Div([
    # Header & filtres
    dbc.Row([
        dbc.Col([
            html.Div(
                children=[
                    dbc.Button(
                        "  Listings  ", outline=False, color="warning", className="me-1", href="/listings",
                        size="lg"),
                    # dbc.Collapse(
                    #    info_button,
                    #    id="navbar-collapse",
                    #    is_open=False
                    # )
                ],
                id='filter_info',
                className="title-box",
            )], xs=4, sm=4, md=4, lg=4, xl=4),
        # Zone filtres Sexe / Catégorie de Poids / Catégorie d'Age / Ligue
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_sexe)],
                multi=False,
                id='my_txt_input1',
                placeholder="Sexe",
            ),
            dcc.Dropdown(
                options=[x for x in sorted(nom_poids)],
                multi=True,
                id='my_txt_input2',
                placeholder="Catégorie Poids"
            )
        ], xs=4, sm=4, md=4, lg=4, xl=4),
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_age)],
                multi=True,
                id='my_txt_input3',
                placeholder="Catégorie Age"),
            dcc.Dropdown(
                options=[x for x in sorted(nom_ligue)],
                multi=True,
                id='my_txt_input4',
                placeholder="Ligue"
            )
        ], xs=4, sm=4, md=4, lg=4, xl=4),
    ]),
    html.Div([
        dcc.Slider(
            df['SaisonAnnee'].min(),
            df['SaisonAnnee'].max(),
            step=1,
            value=df['SaisonAnnee'].max(),
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            id='year-slider',
            className='slider_zone')],
        id='div_output_slider',
        className='slider_box'
    ),

    html.Br(),
    html.Div([
    ],
        id='div_output',
        className='graph_box'
    ),

    html.Div([
        html.Div([
            dash_table.DataTable(
                id='datatable-l',
                # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
                columns=[
                    {"name": i, "id": i, "selectable": True} for i in
                    ['Rang', 'Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'IWF', 'Pays', 'Né le', 'Série', 'Club', 'Date', 'Compet']
                ],
                data=df[(df['Sexe'] == 'M')].to_dict('records'),
                editable=True,
                sort_action="native",
                sort_mode="single",
                style_table={
                    'overflowX': 'scroll'
                },
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'text-align': 'left',
                    'text-indent': '0.2em',
                    'color': 'rgb(80, 80, 90)'
                },
                style_data={
                    'backgroundColor': 'rgb(80, 80, 90)',
                    'color': 'white',
                    'fontWeight': 'light',
                    'font-size': '14px',
                    'border': '1px solid white'
                },
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'minWidth': '40px',
                    'maxWidth': '200px'
                },
                row_selectable=False,
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                style_as_list_view=True,
                page_action="native",
                page_current=0,
                page_size=25,
            ),
        ], className='data_tab_l'),
    ], className='data_tabs'),
    html.Div(id='datatable-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/03_listings.css'
    ),
    html.Div(id='none', children=[], style={'display': 'none'})
],
    id='app_code',
    className='body'
)


@callback(
    Output('my_txt_input1', 'options'),
    [Input('year-slider', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input4', 'value')]
)
def update_datalist(selected_year, txt_inserted2, txt_inserted3, txt_inserted4):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted3:
        filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]

    nom_sexe = list(set(filtered_df['Sexe'].tolist()))
    opt = [x for x in sorted(nom_sexe)]
    return opt

@callback(
    Output('my_txt_input2', 'options'),
    [Input('year-slider', 'value'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input4', 'value')]
)

def update_datalist(selected_year, txt_inserted1, txt_inserted3, txt_inserted4):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted3:
        filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]

    nom_poids = list(set(filtered_df['CatePoids'].tolist()))
    opt = [x for x in sorted(nom_poids)]
    return opt

@callback(
    Output('my_txt_input3', 'options'),
    [Input('year-slider', 'value'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input4', 'value')]
)
def update_datalist(selected_year, txt_inserted1, txt_inserted2, txt_inserted4):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]

    nom_age = list(set(filtered_df['CateAge'].tolist()))
    opt = [x for x in sorted(nom_age)]
    return opt

@callback(
    Output('my_txt_input4', 'options'),
    [Input('year-slider', 'value'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input3', 'value')]
)
def update_datalist(selected_year, txt_inserted1, txt_inserted2, txt_inserted3):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted3:
        filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]

    nom_ligue = list(set(filtered_df['Ligue'].tolist()))
    opt = [x for x in sorted(nom_ligue)]
    return opt

@callback(
    [Output('datatable-l', "data"),
     Output('datatable-l', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input1', component_property='value'),  # sexe
     Input(component_id='my_txt_input2', component_property='value'),  # poids
     Input(component_id='my_txt_input3', component_property='value'),  # age
     Input(component_id='my_txt_input4', component_property='value')  # ligue
     ])
def update_data(selected_year, txt_inserted1, txt_inserted2, txt_inserted3, txt_inserted4):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if not txt_inserted2:
        filtered_df = filtered_df[(filtered_df['RowNumMaxSaison'] == 1)]
    if txt_inserted3:
        filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
        filtered_df = filtered_df.sort_values(by=['Total'], ascending=False)
    if not txt_inserted2:
        filtered_df = filtered_df.sort_values(by=['Max IWF Saison'], ascending=False)

    filtered_df['Rang'] = filtered_df.groupby(['SaisonAnnee']).cumcount()+1
    columns = [
        {"name": i, "id": i, "selectable": True} for i in
        ['Rang', 'Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'IWF', 'Pays', 'Né le', 'Série', 'Club', 'Date', 'Compet']
    ]

    dat = filtered_df.to_dict('records')

    return dat, columns


if __name__ == '__main__':
    run_server(debug=True)
