import dash
import plotly.express as px
from dash import dash_table, dcc, html, callback, clientside_callback
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
import dash_ag_grid as dag
import numpy as np
import os
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_daq as daq
from flask import Flask, render_template

# Connection à la base SQLite
dirname = os.path.dirname(__file__)
path_db = os.path.join(dirname, 'dataltero.db')
conn = sql.connect(database=path_db)

# Requête TODO : associer les max IWF à une compétition précise (lieu, date...) dans la BDD
qry = """SELECT * FROM
            (SELECT distinct
                ath.Nom                         as "Nom"
            ,   substr(ath.DateNaissance, 7, 4) as "Né en"
            ,   ath."Nationalite"               as "Pays"
            ,   clb.Club                        as "Club"
            ,   clb.Ligue                       as "Ligue"
            ,   cat."Sexe"                      as "Sexe"
            ,   cat."Serie"                     as "Serie"
            ,   cat.RangSerie                   as "RangSerie"
            ,   cat."CatePoids"                 as "CatePoids"
            ,   cat."CateAge"                   as "CateAge"
            ,   cat."CateMaster"                as "CateMaster"
            ,   cat.Arrache                     as "Arr"
            ,   cat.EpJete                      as "EpJ"
            ,   cat.PoidsTotal                  as "Total"
            ,   cat.TotalU13                    as "Tot U13"
            ,   cat.PoidsDeCorps                as "PdC"
            ,   cat.IWF_Calcul                  as "IWF"
            ,   cat.IWF_CalculU13               as "IWF U13"
            ,   ' ' || cmp.NomCompetitionCourt  as "Compet"
            ,   cmp.DateCompet                  as "Date"
            ,   apr.SaisonAnnee                 as "SaisonAnnee"
            ,   apr.MaxIWFSaison                as "Max IWF Saison"
            ,   apr.MaxIWF                      as "Max IWF"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee", cat.CatePoids
                                  order by cat.PoidsTotal desc)
                                                as "RowNumMaxCateTotal"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee"
                                  order by cat.IWF_Calcul desc)
                                                as "RowNumMaxSaison"
          FROM ATHLETE as ath 
          LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
          LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
          LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
          LEFT JOIN ATHLETE_PR as apr on apr.AthleteID = ath.AthleteID and apr.SaisonAnnee = cmp.SaisonAnnee)
      """

df = pd.read_sql_query(qry, conn)

df = df.sort_values(by=['RangSerie'])
df['Max IWF Saison'] = round(df['Max IWF Saison'], 3) # Arrondi à 3 virgule pour l'IWF pour le display
df['Max IWF'] = round(df['Max IWF'], 3)
df['IWF U13'] = round(df['IWF U13'], 3)
df['IWF'] = round(df['IWF'], 3)
updated_title = 'Listings'

# app = dash.Dash(__name__)
dash.register_page(__name__, name='3PR - Listings', title='3PR - Listings', image='/assets/3PR.png', description='Listings et classements des haltérophiles français')
# server = server


# df_unique_names = df['Nom'].unique  # Fetch or generate data from Python
nom_ligue = list(set(df['Ligue'].tolist()))
nom_age = list(set(df['CateAge'].tolist()))
nom_age_masters = list(set(df['CateMaster'].tolist()))
nom_poids = list(set(df['CatePoids'].tolist()))
nom_sexe = list(set(df['Sexe'].tolist()))
nom_nat = list(set(df['Pays'].tolist()))
nom_serie = df['Serie'].unique().tolist()
nom_competition = ['Critérium National', 'Chpt Province', 'Chpt Ligue', 'Challenge Avenir', 'Chpt Départemental',  'Cpe de France', 'France Elite', 'Fédéral', 'TOP 9', 'NAT 1', 'NAT 2', 'REG 1',
                   'Monde', 'Trophée Nat']

# body
layout = html.Div([
    # Header & filtres
    dbc.Row([
        dbc.Col([
            html.Div(
                children=[
                    dbc.Button(
                        "  Listings  ", outline=False, color="warning", className="title-box",  href="/listings", size="lg"),
                ],
                id='filter_info',
            )], xs=6, sm=6, md=3, lg=2, xl=2),
        # Zone filtres Sexe / Catégorie de Poids / Catégorie d'Age / Ligue
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_sexe)],
                multi=False,
                id='my_txt_input1',
                placeholder="Sexe",
                className="input-box"
            )
        ], xs=3, sm=3, md=1, lg=1, xl=1),
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_nat)],
                multi=True,
                id='my_txt_input5',
                placeholder="Nationalité",
                className="input-box",
                )
        ], xs=3, sm=3, md=2, lg=2, xl=2),
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_poids)],
                multi=True,
                id='my_txt_input2',
                placeholder="Catégorie Poids",
                className="input-box"
            )
        ], xs=6, sm=6, md=3, lg=3, xl=3),
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_age)],
                multi=True,
                id='my_txt_input3',
                placeholder="Catégorie Age",
                className="input-box",
                ),
        ], xs=6, sm=6, md=3, lg=3, xl=3),
        dbc.Col([
        ], xs=0, sm=0, md=0, lg=2, xl=2),
        #]),
        #dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in sorted(nom_ligue)],
                multi=True,
                id='my_txt_input4',
                placeholder="Ligue",
                className="input-box"
            )
        ], xs=6, sm=6, md=3, lg=3, xl=3),
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in nom_serie],
                multi=True,
                id='my_txt_input6',
                placeholder="Série",
                className="input-box"
            )
        ], xs=6, sm=6, md=3, lg=3, xl=3),
        dbc.Col([
            dcc.Dropdown(
                options=[x for x in nom_competition],
                multi=True,
                id='my_txt_input7',
                placeholder="Compétition",
                className="input-box"
            )
        ], xs=12, sm=12, md=6, lg=3, xl=3),
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.Div([
                daq.BooleanSwitch(id='bool_masters',
                                  on=False,
                                  color="#FFC107"),
                html.P("Masters"),
                ], id="div_masters", className="bool_switch"),
        ], xs=3, sm=3, md=2, lg=2, xl=1),
        dbc.Col([
            dbc.Button("↪️", id="reset_col_list", color="light", outline=True, className="mt-auto", size="sm"),
            dbc.Button("💾", id="excel_export_list", color="light", outline=True, className="mt-auto", size="sm"),
        ], xs=3, sm=3, md=2, lg=2, xl=1),
        dbc.Col([
            dcc.Slider(
                min=df['SaisonAnnee'].min(),
                max=df['SaisonAnnee'].max(),
                step=1,
                value=df['SaisonAnnee'].max(),
                #marks={str(year): {'label': str(year),  'style': {'color': 'white'}} for year in df['SaisonAnnee'].unique()},
                marks=None,
                tooltip={"placement": "bottom", "always_visible": True},
                id='year-slider',
                className='slider_zone')
        ], xs=6, sm=6, md=8, lg=8, xl=10),
    ]),

    html.Br(),
    html.Div([
    ],
        id='div_output',
        className='graph_box'
    ),

    html.Div([
        dag.AgGrid(
            id="ag-datatable-l",
            rowData=df.to_dict("records"),  # **need it
            columnDefs=[],
            defaultColDef={"resizable": True, "sortable": True, "filter": False},
            suppressDragLeaveHidesColumns=True,
            style={"height": 540},
            dashGridOptions={"pagination": False},
            className="ag-theme-quartz-dark",  # https://dashaggrid.pythonanywhere.com/layout/themes
        )
    ]),
    html.Div(id='datatable-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/03_listings.css'
    ),
    html.Br(),
    html.Div(id='none', children=[], style={'display': 'none'})
    ],
    id='app_code_l',
    className='body'
)


@callback(
    Output('my_txt_input1', 'options'),
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input4', 'value'),
     Input('my_txt_input5', 'value'),
     Input('my_txt_input6', 'value')]
)
def update_datalist(selected_year, on, txt_inserted2, txt_inserted3, txt_inserted4, txt_inserted5, txt_inserted6):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted3:
        if on == False:
            filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
        else:
            filtered_df = filtered_df[(filtered_df['CateMaster'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
    if txt_inserted5:
        filtered_df = filtered_df[(filtered_df['Pays'].isin(txt_inserted5))]
    if txt_inserted6:
        filtered_df = filtered_df[(filtered_df['Serie'].isin(txt_inserted6))]

    nom_sexe = list(set(filtered_df['Sexe'].tolist()))
    opt = [x for x in sorted(nom_sexe)]
    return opt

@callback(
    Output('my_txt_input2', 'options'),
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input4', 'value'),
     Input('my_txt_input5', 'value'),
     Input('my_txt_input6', 'value')]
)

def update_datalist(selected_year, on, txt_inserted1, txt_inserted3, txt_inserted4, txt_inserted5, txt_inserted6):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted3:
        if on == False:
            filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
        else:
            filtered_df = filtered_df[(filtered_df['CateMaster'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
    if txt_inserted5:
        filtered_df = filtered_df[(filtered_df['Pays'].isin(txt_inserted5))]
    if txt_inserted6:
        filtered_df = filtered_df[(filtered_df['Serie'].isin(txt_inserted6))]

    nom_poids = list(set(filtered_df['CatePoids'].tolist()))
    opt = [x for x in sorted(nom_poids)]
    return opt

@callback(
    Output('my_txt_input3', 'options'),
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input4', 'value'),
     Input('my_txt_input5', 'value'),
     Input('my_txt_input6', 'value')]
)
def update_datalist(selected_year, on, txt_inserted1, txt_inserted2, txt_inserted4, txt_inserted5, txt_inserted6):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
    if txt_inserted5:
        filtered_df = filtered_df[(filtered_df['Pays'].isin(txt_inserted5))]
    if txt_inserted6:
        filtered_df = filtered_df[(filtered_df['Serie'].isin(txt_inserted6))]

    if on == False:
        nom_age = list(set(filtered_df['CateAge'].tolist()))
    else:
        nom_age = list(set(filtered_df['CateMaster'].tolist()))
    opt = [x for x in sorted(nom_age)]
    return opt

@callback(
    Output('my_txt_input4', 'options'),
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input5', 'value'),
     Input('my_txt_input6', 'value')],
    prevent_initial_call=True
)
def update_datalist(selected_year, on, txt_inserted1, txt_inserted2, txt_inserted3, txt_inserted5, txt_inserted6):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted3:
        if on == False:
            filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
        else:
            filtered_df = filtered_df[(filtered_df['CateMaster'].isin(txt_inserted3))]
    if txt_inserted5:
        filtered_df = filtered_df[(filtered_df['Pays'].isin(txt_inserted5))]
    if txt_inserted6:
        filtered_df = filtered_df[(filtered_df['Serie'].isin(txt_inserted6))]

    nom_ligue = list(set(filtered_df['Ligue'].tolist()))
    opt = [x for x in sorted(nom_ligue)]
    return opt

@callback(
    Output('my_txt_input5', 'options'),
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input4', 'value'),
     Input('my_txt_input6', 'value')]
)
def update_datalist(selected_year, on, txt_inserted1, txt_inserted2, txt_inserted3, txt_inserted4, txt_inserted6):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted3:
        if on == False:
            filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
        else:
            filtered_df = filtered_df[(filtered_df['CateMaster'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
    if txt_inserted6:
        filtered_df = filtered_df[(filtered_df['Serie'].isin(txt_inserted6))]

    nom_nat = list(set(filtered_df['Pays'].tolist()))
    opt = [x for x in sorted(nom_nat)]
    return opt
@callback(
    Output('my_txt_input6', 'options'),
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input('my_txt_input1', 'value'),
     Input('my_txt_input2', 'value'),
     Input('my_txt_input3', 'value'),
     Input('my_txt_input4', 'value'),
     Input('my_txt_input5', 'value')]
)
def update_datalist(selected_year, on, txt_inserted1, txt_inserted2, txt_inserted3, txt_inserted4, txt_inserted5):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
    if txt_inserted3:
        if on == False:
            filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
        else:
            filtered_df = filtered_df[(filtered_df['CateMaster'].isin(txt_inserted3))]
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
    if txt_inserted5:
        filtered_df = filtered_df[(filtered_df['Pays'].isin(txt_inserted5))]

    filtered_df = filtered_df.sort_values(by=['RangSerie'])
    nom_serie = filtered_df['Serie'].unique().tolist()
    opt = [x for x in nom_serie]
    return opt

@callback(
    [Output('ag-datatable-l', "rowData"),
     Output('ag-datatable-l', "columnDefs"),
     Output('ag-datatable-l', "defaultColDef")],
    [Input('year-slider', 'value'),
     Input('bool_masters', 'on'),
     Input(component_id='my_txt_input1', component_property='value'),  # sexe
     Input(component_id='my_txt_input2', component_property='value'),  # poids
     Input(component_id='my_txt_input3', component_property='value'),  # age
     Input(component_id='my_txt_input4', component_property='value'),  # ligue
     Input(component_id='my_txt_input5', component_property='value'),  # nationalité
     Input(component_id='my_txt_input6', component_property='value'),  # série
     Input(component_id='my_txt_input7', component_property='value'),  # compétition
     Input("display", "children") #taille écran
     ])

def update_data(selected_year, on, txt_inserted1, txt_inserted2, txt_inserted3, txt_inserted4, txt_inserted5, txt_inserted6, txt_inserted7, breakpoint_str):
    #on bloque le déplacement de colonne si l'écran est trop petit
    if breakpoint_str == "sm" or breakpoint_str == "xs":
        col_move = True
    else:
        col_move = False
    defaultColDef={"resizable": True, "sortable": True, "filter": True, "suppressMovable": col_move}


    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Sexe'] == txt_inserted1)]
        print(txt_inserted1)
    if not (txt_inserted2 or txt_inserted6 or txt_inserted7):
        filtered_df = filtered_df[(filtered_df['RowNumMaxSaison'] == 1)]
    if txt_inserted2 and not(txt_inserted7):
        filtered_df = filtered_df[(filtered_df['RowNumMaxCateTotal'] == 1)]
    if txt_inserted2:
        filtered_df = filtered_df[(filtered_df['CatePoids'].isin(txt_inserted2))]
        filtered_df = filtered_df.sort_values(by=['Total', 'IWF'], ascending=[False, False])
        print(txt_inserted2)
    # Gestion spécifique masters
    if on == True:
        filtered_df = filtered_df[(filtered_df['CateMaster'].str.len()>0)]
    if txt_inserted3:
        if on == False:
            filtered_df = filtered_df[(filtered_df['CateAge'].isin(txt_inserted3))]
        else:
            filtered_df = filtered_df[(filtered_df['CateMaster'].isin(txt_inserted3))]
        print(txt_inserted3)
    if txt_inserted4:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted4))]
        print(txt_inserted4)
    if txt_inserted5:
        filtered_df = filtered_df[(filtered_df['Pays'].isin(txt_inserted5))]
        print(txt_inserted5)
    if txt_inserted6 and not(txt_inserted7):
        filtered_df = filtered_df[(filtered_df['RowNumMaxCateTotal'] == 1)]
    if txt_inserted6:
        filtered_df = filtered_df.sort_values(by=['IWF', 'Total'], ascending=[False, False])
        filtered_df = filtered_df[(filtered_df['Serie'].isin(txt_inserted6))]
        print(txt_inserted6)
    if txt_inserted7:
        filtered_df = filtered_df[(filtered_df['Compet'].str.contains('|'.join(txt_inserted7)))]
        print(txt_inserted7)
    if not (txt_inserted2 or txt_inserted6):
        filtered_df = filtered_df.sort_values(by=['IWF', 'Total'], ascending=[False, False])
    filtered_df['Rang'] = filtered_df.groupby(['SaisonAnnee']).cumcount()+1

    columns = [
        {
            "headerName": "Athlete",
            "children": [
                {"field": "Rang", "width": 30, "pinned": "left", "hide": False},
                {"field": "Nom", "width": 160, "pinned": "left", "hide": False},

            ],
        },
        {
            "headerName": "Performance",
            "children": [
                {"field": "Arr", "width": 60},
                {"field": "EpJ", "width": 60},
                {"field": "Total", "width": 60, "hide": False},
                {"field": "Tot U13", "width": 80, "hide": True},
                {"field": "IWF", "width": 80, "hide": False},
                {"field": "IWF U13", "width": 80, "hide": True},
                {"field": "PdC", "width": 80},
                {"field": "Serie", "width": 80},
            ],
        },
        {
            "headerName": "Compétition",
            "children": [
                {"field": "Date", "width": 100, "hide": False},
                {"field": "Compet", "width": 250, "hide": False},
            ],
        }, {
            "headerName": "Infos",
            "children": [
                {"field": "Né en", "width": 70, "hide": False},
                {"field": "Pays", "width": 60, "hide": False},
                {"field": "Club", "width": 160, "hide": False},
            ],
        },
    ]

    # Classement spécifique U10 / U13
    l1 = ['U10']
    l2 = ['U10', 'U13']
    l3 = ['U13']
    if txt_inserted3:
        if txt_inserted3 == l1 or txt_inserted3 == l2 or txt_inserted3 == l3:
            print(txt_inserted3)
            if txt_inserted2:
                filtered_df = filtered_df.sort_values(by=['Tot U13', 'IWF U13'], ascending=[False, False])
            else:
                filtered_df = filtered_df.sort_values(by=['IWF U13', 'Tot U13'], ascending=[False, False])
            columns = [
                {
                    "headerName": "Athlete",
                    "children": [
                        {"field": "Rang", "width": 30, "pinned": "left", "hide": False},
                        {"field": "Nom", "width": 160, "pinned": "left", "hide": False},

                    ],
                },
                {
                    "headerName": "Performance",
                    "children": [
                        {"field": "Arr", "width": 60, "hide": False},
                        {"field": "EpJ", "width": 60, "hide": False},
                        {"field": "Total ", "width": 60, "hide": True},
                        {"field": "Tot U13", "width": 80, "hide": False},
                        {"field": "IWF", "width": 80, "hide": True},
                        {"field": "IWF U13", "width": 80, "hide": False},
                        {"field": "PdC", "width": 80, "hide": False},
                        {"field": "Serie", "width": 80, "hide": False},
                    ],
                },
                {
                    "headerName": "Compétition",
                    "children": [
                        {"field": "Date", "width": 100, "hide": False},
                        {"field": "Compet", "width": 250, "hide": False},
                    ],
                }, {
                    "headerName": "Infos",
                    "children": [
                        {"field": "Né en", "width": 70, "hide": False},
                        {"field": "Pays", "width": 60, "hide": False},
                        {"field": "Club", "width": 160, "hide": False},
                    ],
                },
            ]


    dat = filtered_df.to_dict('records')

    return dat, columns, defaultColDef

@callback(
    Output("ag-datatable-l", "columnDefs", allow_duplicate=True),
    [Input("reset_col_list", "n_clicks")],
    prevent_initial_call=True
)

def toggle_modal_athl(reset_l_clicks):
    if reset_l_clicks:
        cols = [
                {
                "headerName": "Athlete",
                "children": [
                    {"field": "Rang", "width": 30, "pinned": "left", "hide": False},
                    {"field": "Nom", "width": 160, "pinned": "left", "hide": False},

                ],
            },
            {
                "headerName": "Performance",
                "children": [
                    {"field": "Arr", "width": 60, "hide": False},
                    {"field": "EpJ", "width": 60, "hide": False},
                    {"field": "Total", "width": 60},
                    {"field": "Tot U13", "width": 80},
                    {"field": "IWF", "width": 80},
                    {"field": "IWF U13", "width": 80},
                    {"field": "PdC", "width": 80, "hide": False},
                    {"field": "Serie", "width": 80, "hide": False},
                ],
            },
            {
                "headerName": "Compétition",
                "children": [
                    {"field": "Date", "width": 100, "hide": False},
                    {"field": "Compet", "width": 250, "hide": False},
                ],
            },            {
                "headerName": "Infos",
                "children": [
                    {"field": "Né en", "width": 70, "hide": False},
                    {"field": "Pays", "width": 60, "hide": False},
                    {"field": "Club", "width": 160, "hide": False},
                ],
            },
        ]

    return cols

@callback(
    [Output("app_code_l", "className"),
     Output("ag-datatable-l", "className"),
     Output("reset_col_list", "color"),
     Output("div_masters", "className")],
    [Input("bool_light", "on")]
)

def light_mode_list(on):

    #masters_label_pos = "bottom"
    if on == True:
        css_body = "body_light"
        css_grid = "ag-theme-quartz"
        reset_color = "secondary"
        masters_label_classname = "bool_switch_light"
    else:
        css_body = "body"
        css_grid = "ag-theme-quartz-dark"
        reset_color = "light"
        masters_label_classname = "bool_switch"

    return css_body, css_grid, reset_color, masters_label_classname;

#Export Excel
clientside_callback(
    """async function (n) {
        if (n) {
            grid1Api = await dash_ag_grid.getApiAsync("ag-datatable-l")
            var spreadsheets = [];

            spreadsheets.push(
              grid1Api.getSheetDataForExcel({ sheetName: 'Listings' })
            );

            grid1Api.exportMultipleSheetsAsExcel({
              data: spreadsheets,
              fileName: 'listings.xlsx',
            });
        }
        return dash_clientside.no_update
    }""",
    Output("excel_export_list", "n_clicks"),
    Input("excel_export_list", "n_clicks"),
    prevent_initial_call=True
)

if __name__ == '__main__':
    run_server(debug=True)
