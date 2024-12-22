import dash
import plotly.express as px
from dash import dash_table, dcc, html, callback, State, clientside_callback
from dash.exceptions import PreventUpdate
from datetime import date, datetime
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

# Requête TODO : associer les IWF Max à une compétition précise (lieu, date...) dans la BDD
qry = """SELECT * FROM REPORT_LISTINGS"""

df = pd.read_sql_query(qry, conn)

df = df.sort_values(by=['RangSerie'])
df['IWF Max Saison'] = round(df['IWF Max Saison'], 3) # Arrondi à 3 virgule pour l'IWF pour le display
df['IWF Max'] = round(df['IWF Max'], 3)
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
nom_saison = df['SaisonAnnee'].unique().tolist()
list_names = df['Nom'].unique().tolist()
nom_competition = ['Critérium National', 'Chpt Province', 'Chpt Ligue', 'Challenge Avenir', 'Chpt Départemental',  'Cpe de France', 'France Elite', 'Fédéral', 'TOP 9', 'NAT 1', 'NAT 2', 'REG 1',
                   'Monde', 'Tournoi International', 'Trophée Nat']

init_curr_year = datetime.now().year
curr_year = init_curr_year
curr_month = datetime.now().month
if curr_month>8:
    curr_year=curr_year+1

# body
layout = html.Div([
    # Header & filtres
    dcc.Store(id='df_quizz', data={}, storage_type='memory'),
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
        ], xs=6, sm=6, md=3, lg=3, xl=3),
        dbc.Col([
            html.Div([
                dcc.DatePickerRange(
                    id='filtre_dates',
                    min_date_allowed=date(curr_year-1, 9, 1),
                    max_date_allowed=date(curr_year, 8, 31),
                    initial_visible_month=date(init_curr_year, curr_month, 1),
                    start_date=date(curr_year-1, 9, 1),
                    end_date=date(curr_year, 8, 31),
                    display_format="DD/MM/YYYY",
                    start_date_placeholder_text="Date Début",
                    end_date_placeholder_text="Date Fin"
                )
            ], id="date_pick", className="date-pick"
        ),
        ], xs=6, sm=6, md=3, lg=3, xl=3),

    ]),

    html.Br(),
    #master Switch
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
            dbc.Button("🎯 Quizz", id="quizz", color="light", outline=True, className="me-1", size="sm"),
        ], xs=3, sm=3, md=2, lg=2, xl=2),

        dbc.Col([
            dbc.Modal([
                dbc.ModalHeader("🎯 Quizz - Top 10"),
                dbc.ModalBody([
                    html.P("Choisissez vos options et cliquez sur 'Lancer'. Essayez de deviner tous les athlètes qui composent le Top 10. Seuls les athlètes de nationalité française sont inclus."),
                    dcc.Dropdown(
                        options=[x for x in sorted(nom_sexe)],
                        multi=False,
                        id='quizz_input_s',
                        placeholder="Sexe",
                        className="input-box"
                    ),
                    dcc.Dropdown(
                        options=[x for x in ["SEN", "U15", "U17", "U20"]],
                        multi=False,
                        id='quizz_input_a',
                        placeholder="Catégorie Age",
                        className="input-box",
                    ),
                    dcc.Dropdown(
                        options=[x for x in [2022, 2023, 2024, 2025]],
                        multi=False,
                        id='quizz_input_sa',
                        placeholder="Saison",
                        className="input-box",
                    ),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("▶️ Lancer", id="lancer_quizz", color="secondary", outline=True, className="me-1", size="sm"),
                            html.Div([
                                dbc.Button("🏳️ Abandonner", id="stop_quizz", color="secondary", outline=True, className="me-1", size="sm"),
                            ], id="button_stop", style={'display': 'none'}),
                        ], xs=12, sm=12, md=10, lg=8, xl=6),
                    ]),

                html.P(""),
                html.P("", id="txt_q_titre"),
                html.Div([
                    dcc.Dropdown(
                            options=[x for x in sorted(list_names)],
                            multi=False,
                            id='q_athlete_input',
                            value='',
                            placeholder="Choisir des athlètes...",
                            className="input_box1",
                            ),
                    ], id="div_q_athlete", style={'display': 'none'}),
                html.P("", id="txt_reponse"),
                html.Div([
                    html.P("🥇 #1 ", id="n1", style={'color':'black'}),
                    html.P("🥈 #2 ", id="n2", style={'color':'black'}),
                    html.P("🥉 #3 ", id="n3", style={'color':'black'}),
                    html.P("#4 ", id="n4", style={'color':'black'}),
                    html.P("#5 ", id="n5", style={'color':'black'}),
                    html.P("#6 ", id="n6", style={'color':'black'}),
                    html.P("#7 ", id="n7", style={'color':'black'}),
                    html.P("#8 ", id="n8", style={'color':'black'}),
                    html.P("#9 ", id="n9", style={'color':'black'}),
                    html.P("#10 ", id="n10", style={'color':'black'})],
                id="txt_quizz",
                style={'display': 'none', 'color':'black'}),
                ]),
                dbc.ModalFooter(
                    dbc.Button("Fermer", id="close-button-q", color="secondary", className="ml-auto", size="sm")
                ),
            ], id="quizz-modal", size="lg", centered=True, is_open=False),
        ], width="auto"),


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
        ], xs=5, sm=5, md=6, lg=6, xl=8),
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
                {"field": "Club", "width": 200, "hide": False},
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
            filtered_df['Rang'] = filtered_df.groupby(['SaisonAnnee']).cumcount() + 1
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
                        {"field": "Club", "width": 200, "hide": False},
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
                    {"field": "Club", "width": 200, "hide": False},
                ],
            },
        ]

    return cols

@callback(
    [Output("app_code_l", "className"),
     Output("ag-datatable-l", "className"),
     Output("reset_col_list", "color"),
     Output("excel_export_list", "color"),
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

    return css_body, css_grid, reset_color, reset_color, masters_label_classname

#Bouton Quizz
@callback(
    Output("quizz-modal", "is_open"),
    [Input("quizz", "n_clicks"),
    Input("close-button-q", "n_clicks")],
    State("quizz-modal", "is_open"),
    prevent_initial_call=True
)

def toggle_info_modal(open_clicks_q, close_clicks_q, is_open_q):
    if open_clicks_q or close_clicks_q:
        return not is_open_q
    print(str(is_open_q))
    return is_open_q

#Lancer Quizz
@callback(
        [Output("txt_reponse", "children"),
         Output("button_stop", "style"),
         Output("txt_quizz", "style"),
         Output("div_q_athlete", "style"),
         Output("txt_q_titre", "children"),
         Output("df_quizz", "data"),
         Output("lancer_quizz", "n_clicks"),
         Output("n1", "children", allow_duplicate=True),
         Output("n2", "children", allow_duplicate=True),
         Output("n3", "children", allow_duplicate=True),
         Output("n4", "children", allow_duplicate=True),
         Output("n5", "children", allow_duplicate=True),
         Output("n6", "children", allow_duplicate=True),
         Output("n7", "children", allow_duplicate=True),
         Output("n8", "children", allow_duplicate=True),
         Output("n9", "children", allow_duplicate=True),
         Output("n10", "children", allow_duplicate=True),
         Output("n1", "style", allow_duplicate=True),
         Output("n2", "style", allow_duplicate=True),
         Output("n3", "style", allow_duplicate=True),
         Output("n4", "style", allow_duplicate=True),
         Output("n5", "style", allow_duplicate=True),
         Output("n6", "style", allow_duplicate=True),
         Output("n7", "style", allow_duplicate=True),
         Output("n8", "style", allow_duplicate=True),
         Output("n9", "style", allow_duplicate=True),
         Output("n10", "style", allow_duplicate=True)],
        [Input("lancer_quizz", "n_clicks"),
         Input("quizz_input_s", "value"),
         Input("quizz_input_a", "value"),
         Input("quizz_input_sa", "value")],
    prevent_initial_call=True
)

def quizz_lancer(q_is_started, val_sexe, val_age, val_saisonannee):
    #On ne relance pas le quizz si changement de catégori
    if not q_is_started:
        raise PreventUpdate
    display_opt = {'display': 'none', 'color': 'black'}
    out_init = ['']*10
    txt_out=''
    df_q = pd.DataFrame()
    txt_q_titre = ''
    for i in range(0,10):
        if i == 0:
            out_init[i] = "🥇 #1 "
        elif i == 1:
            out_init[i] = "🥈 #2 "
        elif i == 2:
            out_init[i] = "🥉 #3 "
        else:
            out_init[i]='#' + str(i+1) + ' '

    if q_is_started:
        txt_out="C'est parti !"
        where_qry_quizz = " where ath.""Nationalite""='FR' and cat.Sexe = '" + val_sexe + "'"
        join_athl_pr=""
        order_by = " order by apr.""MaxIWF"" desc "
        if val_age:
            where_qry_quizz = where_qry_quizz + " and CateAge = '" + val_age + "'"
        if val_saisonannee:
            where_qry_quizz = where_qry_quizz + " and cmp.SaisonAnnee = " + str(val_saisonannee) + ""
            join_athl_pr = " and apr.SaisonAnnee = cmp.SaisonAnnee"
            order_by = " order by apr.""MaxIWFSaison"" desc "

        display_opt = {'display': 'block', 'color':'black'}
        print(where_qry_quizz)
        qry_quizz = """SELECT * FROM
                        (SELECT distinct
                            ath.Nom                         as "Nom"
                      FROM ATHLETE as ath 
                      LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                      LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                      LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
                      LEFT JOIN ATHLETE_PR as apr on apr.AthleteID = ath.AthleteID"""\
                     + join_athl_pr + where_qry_quizz + order_by + """)
                  """
        # Connection à la base SQLite
        txt_q_titre = 'Top 10 '
        if val_sexe=='F':
            txt_q_titre = txt_q_titre + 'Femmes '
        elif val_sexe=='M':
            txt_q_titre = txt_q_titre + 'Hommes '
        if val_age :
            txt_q_titre = txt_q_titre + val_age + ' '
        if val_saisonannee:
            txt_q_titre = txt_q_titre + 'Saison ' + str(val_saisonannee-1) + '-' + str(val_saisonannee)
        else:
            txt_q_titre = txt_q_titre + 'sur toutes les saisons (2021+) '

        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        df_q = pd.read_sql_query(qry_quizz, conn)
        print(df_q)
    return txt_out, display_opt, display_opt,  display_opt, txt_q_titre, df_q.to_dict('records'), 0, \
        out_init[0], out_init[1], out_init[2], out_init[3], out_init[4], out_init[5], out_init[6], out_init[7], out_init[8], out_init[9], \
        display_opt, display_opt, display_opt, display_opt, display_opt, display_opt, display_opt, display_opt, display_opt, display_opt

@callback(
    [Output("txt_reponse", "children", allow_duplicate=True),
     Output("q_athlete_input", "value"),
     Output("stop_quizz", "n_clicks", allow_duplicate=True),
     Output("n1", "children", allow_duplicate=True),
     Output("n2", "children", allow_duplicate=True),
     Output("n3", "children", allow_duplicate=True),
     Output("n4", "children", allow_duplicate=True),
     Output("n5", "children", allow_duplicate=True),
     Output("n6", "children", allow_duplicate=True),
     Output("n7", "children", allow_duplicate=True),
     Output("n8", "children", allow_duplicate=True),
     Output("n9", "children", allow_duplicate=True),
     Output("n10", "children", allow_duplicate=True)],
     [Input("q_athlete_input", "value"),
      Input("df_quizz", "data"),
      Input("n1", "children"),
      Input("n2", "children"),
      Input("n3", "children"),
      Input("n4", "children"),
      Input("n5", "children"),
      Input("n6", "children"),
      Input("n7", "children"),
      Input("n8", "children"),
      Input("n9", "children"),
      Input("n10", "children")
      ],
     allow_duplicates=True,
     prevent_initial_call=True)

def update_quizz(q_athlete, df_q, n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, n_9, n_10):
    if q_athlete == '':
        raise PreventUpdate
    print(q_athlete),
    df_q_df = pd.DataFrame(df_q)
    force_stop = 0
    out = [''] * 10
    txt_out=''
    q_value_cleaning = ''
    a=0
    if q_athlete != '':
        txt_out = q_athlete + " n'est pas dans la liste"
    for i in range(0, 10):
        print(i)
        print(df_q_df['Nom'].values[i])
        out[i] = str(locals()["n_" + str(i + 1)])
        if q_athlete == df_q_df['Nom'].values[i] and len(out[i])>=8:
            a=a+1
            txt_out = q_athlete + " a déjà été trouvé(e)"
        elif q_athlete == df_q_df['Nom'].values[i] and len(out[i])<=8:
            txt_out = "Bien joué, " + df_q_df['Nom'].values[i] + " est #" + str(i+1)
            out[i] = str(locals()["n_" + str(i+1)]) + df_q_df['Nom'].values[i]
            print(str(locals()["n_" + str(i+1)]) + df_q_df['Nom'].values[i])
            a=a+1

    if a == 10:
        force_stop=1
    return txt_out, q_value_cleaning, force_stop, out[0], out[1], out[2], out[3], out[4], out[5], out[6], out[7], out[8], out[9]
@callback(
        [Output("txt_reponse", "children", allow_duplicate=True),
         Output("stop_quizz", "n_clicks"),
         Output("button_stop", "style", allow_duplicate=True),
         Output("div_q_athlete", "style", allow_duplicate=True),
         Output("n1", "children", allow_duplicate=True),
         Output("n2", "children", allow_duplicate=True),
         Output("n3", "children", allow_duplicate=True),
         Output("n4", "children", allow_duplicate=True),
         Output("n5", "children", allow_duplicate=True),
         Output("n6", "children", allow_duplicate=True),
         Output("n7", "children", allow_duplicate=True),
         Output("n8", "children", allow_duplicate=True),
         Output("n9", "children", allow_duplicate=True),
         Output("n10", "children", allow_duplicate=True),
         Output("n1", "style"),
         Output("n2", "style"),
         Output("n3", "style"),
         Output("n4", "style"),
         Output("n5", "style"),
         Output("n6", "style"),
         Output("n7", "style"),
         Output("n8", "style"),
         Output("n9", "style"),
         Output("n10", "style")],
        [Input("stop_quizz", "n_clicks"),
         Input("df_quizz", "data"),
         Input("n1", "children"),
         Input("n2", "children"),
         Input("n3", "children"),
         Input("n4", "children"),
         Input("n5", "children"),
         Input("n6", "children"),
         Input("n7", "children"),
         Input("n8", "children"),
         Input("n9", "children"),
         Input("n10", "children")],
        prevent_initial_call=True
)

def end_quizz(stop_q, df_q, n_1, n_2, n_3, n_4, n_5, n_6, n_7, n_8, n_9, n_10):
    if stop_q is None or stop_q==0:
        print("sttop")
        raise PreventUpdate
    if stop_q:
        df_q_df = pd.DataFrame(df_q)
        cnt_ok = 0
        out = [''] * 10
        style_end=[{'color': 'black'}] * 10
        for i in range(0,10):
            if len(str(locals()["n_" + str(i + 1)]))>8:
                cnt_ok = cnt_ok+1
                out[i] = str(locals()["n_" + str(i + 1)])
            else:
                out[i] = str(locals()["n_" + str(i + 1)]) + df_q_df['Nom'].values[i]
                style_end[i] = {'color': 'red'}

        dict_out = {
            0: "🤡 0/10 - NC : Bravo pour la bulle !",
            1: "😔 1/10 - DEB-48 : C'est catastrophique",
            2: "👎 2/10 - DEB+2 : Peut beaucoup mieux faire",
            3: "🤷 3/10 - DPT+5 : Insuffisant",
            4: "😐 4/10 - REG+12 : Un peu de potentiel",
            5: "👍 5/10 - IRG+0 : La moyenne, c'est pas mal",
            6: "😊 6/10 - FED+7 : C'est prometteur",
            7: "💪 7/10 - NAT+5 : Gros potentiel",
            8: "🤩 8/10 - INT B+0 : Très très fort",
            9: "⭐ 9/10 - INT A+10 : Tu es un puit de connaissances !",
            10: "💯 10/10 - OLY+20 : Tout juste ! Bravo champion !",

        }

        return [dict_out[cnt_ok]], 0, {'display':'none'}, {'display':'none'}, out[0], out[1], out[2], out[3], out[4], out[5], out[6], out[7], out[8], out[9],   \
        style_end[0], style_end[1], style_end[2], style_end[3], style_end[4], style_end[5], style_end[6], style_end[7], style_end[8], style_end[9]

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
