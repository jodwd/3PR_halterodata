import dash
import plotly.express as px
from dash import dash_table, dcc, callback, State, html, clientside_callback
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
import dash_ag_grid as dag
import os
from dash.dependencies import Input, Output
import dash_daq as daq
import dash_bootstrap_components as dbc

# Connection à la base SQLite
dirname = os.path.dirname(__file__)
path_db = os.path.join(dirname, 'dataltero.db')
conn = sql.connect(database=path_db)

# Requête principale
qry = """SELECT ath.Nom, ath.DateNaissance as "Né le"
      , substr(cmp."NomCompetitionCourt", 1, 64) as "Competition", cat."PoidsDeCorps" as "PdC", clb.Club
      , cmp.AnneeMois as "Mois", cmp.SaisonAnnee, cmp.MoisCompet, cmp.DateCompet as "Date", cat.Sexe
      , cat.Arr1, cat.Arr2, cat.Arr3, cat.Arrache as "Arr", cat.Epj1, cat.Epj2, cat.Epj3, cat.EpJete as "EpJ"
      , cat.Serie as "Série", cat.Categorie as "Catégorie", cat.PoidsTotal as "Total", cat.IWF_Calcul as "IWF"             
      ,   ath."MondeSEN",    ath."MondeU20",    ath."MondeU17",    ath."MondeMasters"               
      ,   ath."EuropeSEN",   ath."EuropeU23",   ath."EuropeU20",   ath."EuropeU17",   ath."EuropeMasters"   
      ,   ath."FranceElite",   ath."GrandPrixFederal",   ath."TropheeNationalU13"     
      ,   ath."NbCompet",   ath."Nb6sur6",   ath."Nb2sur6DerniereBarre",   ath."NbBulles",   ath."NbDoublesBulles"
      FROM ATHLETE as ath 
      LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
      LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
      LEFT JOIN CLUB as clb on clb.Club = cat.CATClub"""
df = pd.read_sql_query(qry, conn)
df.head()

# Requête secondaire pour le détail athlète
qry2 = """SELECT ath.Nom, cat.Serie as "Série", cat.Categorie as "Catégorie"
      FROM ATHLETE as ath 
      LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
      LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
      LEFT JOIN CLUB as clb on clb.Club = cat.CATClub"""
df2 = pd.read_sql_query(qry2, conn)
df2.head()

# Reformatage des donnée de la requête
df['IWF'] = round(df['IWF'], 3)
df['MoisCompet'] = pd.Categorical(df['MoisCompet'], ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05", "06", "07"])
df2['Série'] = pd.Categorical(df2['Série'], ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"], ordered=True)
df_temp = df[df['Nom']=='ZZZZZ']
dash.register_page(__name__, path='/', name='3PR - Athletes', title='3PR - Dashboard Athlètes', image='/assets/3PR.png', description='Tableau de bord des performances des haltérophiles français')

# Liste d'athlètes = ceux qui ont tiré sur la plage par défaut càd l'année dernière + l'année en cours
selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
list_names = list(set(df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]['Nom'].tolist()))

# body
layout = html.Div([
    # Header & filtres
        dbc.Row([            # Titre
            dbc.Col([
                dbc.Button(" Dashboard Athlètes ", id="title-box", color="danger", className="titlebox", size="lg"),
                    dbc.Modal([
                        dbc.ModalHeader(" Dashboard Athlètes ", id="athlete_info_"),
                        dbc.ModalBody([
                            html.Div([html.P("Cette page...")]),
                        ]),
                        dbc.ModalFooter(
                            dbc.Button("Fermer", id="close-athlete_info-", color="secondary", className="ml-auto")
                        ),
                    ], id="athlete-info-modal_", size="lg", centered=True, is_open=False),
                ], xs=6, sm=6, md=6, lg=2, xl=2),

            # Zone filtres athlètes
            dbc.Col([
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            options=[x for x in sorted(list_names)],
                            multi=True,
                            id='my_txt_input',
                            placeholder="Choisir des athlètes...",
                            className="input_box1",
                            )
                        ]),
                    #html.Datalist(id='Nom_athl')
                    ])
                ], xs=6, sm=6, md=6, lg=2, xl=2),

            # Cartes athlètes (masquées par défaut)
            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody([
                                html.Div([html.P("Card 1")], id="athlete1_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete1_club"),
                                    html.Div([html.P("NaissanceMax")], id="athlete1_annivmax")
                                  ],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl1", color="danger", className="mt-auto", size="sm"),
                                dbc.Modal([
                                    dbc.ModalHeader([
                                        dbc.ModalTitle("Information", id="athlete1_nom_info", class_name='ath_info_header'),
                                        html.Div([
                                            dbc.Row([
                                                dbc.Col([
                                                    dbc.Button("❓", id="open-aide_achievements-athl1", color="white", className="mt-auto", size="sm"),
                                                    dbc.Modal([
                                                        dbc.ModalHeader([
                                                            dbc.ModalTitle("Information", id="achievement_aide_header_athl1"),
                                                        ]),
                                                        dbc.ModalBody([
                                                            html.P("", id="ach_aide-txt_athl1"),
                                                            html.Div(id="ach_aide-table_athl1"),
                                                        ]),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Fermer", id="close-aide_achievements-athl1", color="secondary", className="ml-auto")
                                                        ),
                                                    ], id="aide_achievements_athl1", size="md", centered=True, is_open=False),
                                                ]),
                                            ], align="right"),
                                        ], id='ach_aide-div_athl1', style= {'display': 'none'})
                                    ]),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl1-graph', style = {'display': 'none'}),
                                        html.Div(id="athl1-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Fermer", id="close-athl1", color="secondary", className="ml-auto")
                                    ),
                                ], id="athl1-modal", size="lg", centered=True, is_open=False),
                            ]
                        ),
                    ),
                ], id="athl_card1",  style= {'display': 'none'}),
            ], xs=6, sm=3, md=3, lg=2, xl=2),
            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div([html.P("Card 2")], id="athlete2_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete2_club"),
                                    html.Div([html.P("NaissanceMax")], id="athlete2_annivmax")],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl2", color="primary", className="mt-auto", size="sm"),
                                dbc.Modal([
                                    dbc.ModalHeader([
                                        dbc.ModalTitle("Information", id="athlete2_nom_info"),
                                        html.Div([
                                            dbc.Row([
                                                dbc.Col([
                                                    dbc.Button("❓", id="open-aide_achievements-athl2", color="white", className="mt-auto", size="sm"),
                                                    dbc.Modal([
                                                        dbc.ModalHeader([
                                                            dbc.ModalTitle("Information", id="achievement_aide_header_athl2"),
                                                        ]),
                                                        dbc.ModalBody([
                                                            html.P("", id="ach_aide-txt_athl2"),
                                                            html.Div(id="ach_aide-table_athl2"),
                                                        ]),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Fermer", id="close-aide_achievements-athl2", color="secondary", className="ml-auto")
                                                        ),
                                                    ], id="aide_achievements_athl2", size="md", centered=True, is_open=False),
                                                ]),
                                            ], align="right"),
                                        ], id='ach_aide-div_athl2', style={'display': 'none'})
                                    ]),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl2-graph', style = {'display': 'none'}),
                                        html.Div(id="athl2-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Fermer", id="close-athl2", color="secondary", className="ml-auto")
                                    ),
                                    ], id="athl2-modal", size="lg", centered=True, is_open=False),
                            ]
                        ),
                    )
                ], id="athl_card2",  style= {'display': 'none'}),
            ], xs=6, sm=3, md=3, lg=2, xl=2),
            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div([html.P("Card 3")], id="athlete3_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete3_club"),
                                    html.Div([html.P("NaissanceMax")], id="athlete3_annivmax")],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl3", color="warning", className="mt-auto", size="sm"),
                                dbc.Modal([
                                    dbc.ModalHeader([
                                        dbc.ModalTitle("Information", id="athlete3_nom_info"),
                                        html.Div([
                                            dbc.Row([
                                                dbc.Col([
                                                    dbc.Button("❓", id="open-aide_achievements-athl3", color="white", className="mt-auto", size="sm"),
                                                    dbc.Modal([
                                                        dbc.ModalHeader([
                                                            dbc.ModalTitle("Information", id="achievement_aide_header_athl3"),
                                                        ]),
                                                        dbc.ModalBody([
                                                            html.P("", id="ach_aide-txt_athl3"),
                                                            html.Div(id="ach_aide-table_athl3"),
                                                        ]),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Fermer", id="close-aide_achievements-athl3", color="secondary", className="ml-auto")
                                                        ),
                                                    ], id="aide_achievements_athl3", size="md", centered=True, is_open=False),
                                                ]),
                                            ], align="right"),
                                        ], id='ach_aide-div_athl3', style={'display': 'none'})
                                    ]),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl3-graph', style = {'display': 'none'}),
                                        html.Div(id="athl3-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Fermer", id="close-athl3", color="secondary", className="ml-auto")
                                    ),
                                    ], id="athl3-modal", size="lg", centered=True, is_open=False),
                            ]
                        ),
                    )
                ], id="athl_card3",  style= {'display': 'none'}),
            ], xs=6, sm=3, md=3, lg=2, xl=2),
            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div([html.P("Card 4")], id="athlete4_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete4_club"),
                                    html.Div([html.P("NaissanceMax")], id="athlete4_annivmax")],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl4", color="success", className="mt-auto", size="sm"),
                                dbc.Modal([
                                    dbc.ModalHeader([
                                        dbc.ModalTitle("Information", id="athlete4_nom_info"),
                                        html.Div([
                                            dbc.Row([
                                            dbc.Col([
                                                dbc.Button("❓", id="open-aide_achievements-athl4", color="white", className="mt-auto", size="sm"),
                                                    dbc.Modal([
                                                        dbc.ModalHeader([
                                                            dbc.ModalTitle("Information", id="achievement_aide_header_athl4"),
                                                        ]),
                                                        dbc.ModalBody([
                                                            html.P("", id="ach_aide-txt_athl4"),
                                                            html.Div(id="ach_aide-table_athl4"),
                                                        ]),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Fermer", id="close-aide_achievements-athl4", color="secondary", className="ml-auto")
                                                        ),
                                                    ], id="aide_achievements_athl4", size="md", centered=True, is_open=False),
                                                ]),
                                            ], align="right"),
                                        ], id='ach_aide-div_athl4', style={'display': 'none'})
                                    ]),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl4-graph', style = {'display': 'none'}),
                                        html.Div(id="athl4-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Fermer", id="close-athl4", color="secondary", className="ml-auto")
                                    ),
                                    ], id="athl4-modal", size="lg", centered=True, is_open=False),
                            ]
                        ),
                    )
                ], id="athl_card4",  style= {'display': 'none'}),
            ], xs=6, sm=3, md=3, lg=2, xl=2),
        ],  className="top_zone",),

    # Zone graph
    html.Br(),
    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(id='bool_total',
                              on=False,
                              label={"label": "IWF/Total", 'style': {"color": "white"}},
                              labelPosition="bottom",
                              color="#DC3545"),
        ], xs=3, sm=3, md=2, lg=2, xl=1),
        dbc.Col([
            dbc.Button("↪️ Reset", id="reset_col", color="light", outline=True, className="mt-auto", size="sm"),
            dbc.Button("💾 Excel", id="excel_export", color="light", outline=True, className="mt-auto", size="sm"),
        ], xs=3, sm=3, md=2, lg=2, xl=1),
        dbc.Col([
            dcc.RangeSlider(
                df['SaisonAnnee'].min(),
                df['SaisonAnnee'].max(),
                step=None,
                value=selected_year,
                marks={str(year): {'label' : str(year), 'style':{'color':'white'}} for year in df['SaisonAnnee'].unique()},
                id='year-slider-athl',
                className='slider_zone'
                ),
            ], xs=6, sm=6, md=8, lg=8, xl=10),
        dbc.Col([
            dcc.Graph(
                id='graph-with-slider',
                style= {'display': 'none'}
                ) ,
        ], width=12),
    ]),

    # Zone data table AG Grid
    html.Br(),
    html.Div([
        dag.AgGrid(
            id = "ag_datatable_athl",
            enableEnterpriseModules=True,
            rowData = df_temp.to_dict("records"),
            columnDefs = [
                        {
                            "headerName": "Athlete",
                            "children": [
                                {"field": "Nom", "width": 200, "pinned": "left", "hide": False},
                                {"field": "PdC", "width": 80, "hide": False},
                                {"field": "Catégorie", "width": 100, "hide": False},
                            ],
                        },
                        {
                            "headerName": "Arraché",
                            "children": [
                                {"field": "Arr1", "headerName": "1", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "Arr2", "headerName": "2", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "Arr3", "headerName": "3", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "Arr", "width": 75, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(235, 61, 85)'} : {'color': 'rgb(59, 113, 202)'}",
                                 },
                                 },
                            ],
                        },
                        {
                            "headerName": "Epaulé Jeté", "hide": False,
                            "children": [
                                {"field": "EpJ1", "headerName": "1", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "EpJ2", "headerName": "2", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "EpJ3", "headerName": "3", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "EpJ", "width": 75, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(235, 61, 85)'} : {'color': 'rgb(59, 113, 202)'}",
                                 },
                                 },
                            ],
                        },
        
                        {
                            "headerName": "Performance",
                            "children": [
                                {"field": "Total", "width": 80, "hide": False, "font-weight": 'bold',
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(255, 41, 65)'} : {'color': 'rgb(44, 98, 217)'}",
                                 },
                                 },
                                {"field": "IWF", "width": 80, "hide": False},
                                {"field": "Série", "width": 80, "hide": False},
                            ],
                        },
                        {
                            "headerName": "Compétition",
                            "children": [
                                {"field": "Date", "width": 150, "hide": False},
                                {"field": "Competition", "hide": False}
                            ],
                        }
                    ],
            defaultColDef = {"resizable": True, "sortable": True, "filter": True},
            suppressDragLeaveHidesColumns=False,
            dashGridOptions = {"pagination": False},
            className = "ag-theme-quartz-dark",  # https://dashaggrid.pythonanywhere.com/layout/themes
        )

    ]),
    html.Br(),
    html.Br(),
    html.Link(
        rel='stylesheet',
        href='/assets/01_dash_board.css'
    )
    ],
    id='app_code_athl',
    className='body'
)

# Mise à jour de la liste d'athlète dispo en fonction des années de référence
@callback(
    Output('my_txt_input', 'options'),
    Input('year-slider-athl', 'value'),
    prevent_initial_call=True
)
def update_athletes_list(selected_year):
    fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    list_names = list(set(fdf['Nom'].tolist()))
    options = [x for x in sorted(list_names)]
    return options

#Mise à jour du graphique
@callback(
    [Output('graph-with-slider', 'figure'),
     Output('graph-with-slider', 'style')],
    [Input('year-slider-athl', 'value'),
     Input('bool_total', 'on'),
     Input('bool_light', 'on'),
     Input(component_id='my_txt_input', component_property='value'),
     Input("reset_col", "n_clicks"),
     Input("display", "children")
     ],
     prevent_initial_call=True)
def update_figure(selected_year, on, on_light, txt_inserted, n_clicks, breakpoint_str):
    if selected_year == '':
        selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
    fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if txt_inserted:
        # On trie par nom pour aligner la saisie, les cartes et le graphique
        fdf = fdf[(fdf['Nom'].isin(txt_inserted))]
        fdf.Nom = fdf.Nom.astype("category")
        fdf.Nom = fdf.Nom.cat.set_categories(txt_inserted)
        fdf = fdf.sort_values(by='Nom')
        if breakpoint_str=="md":
            display_graph = {'display': 'block', 'height': 300}
        else:
            display_graph = {'display': 'block', 'height': '50vh'}

        if on_light == True:
            font_col = 'rgb(40,40,45)'
            plot_col = 'rgb(249, 250, 251)'
        else:
            font_col = "white"
            plot_col = 'rgb(40,40,45)'

        #Paramètres de graph
        if on_light == True:
            color_seq = ["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#282D2D", "purple", "#54B4D3", "#9FA6B2"]
        else:
            color_seq = ["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"]

        if on == True:
            fig = px.scatter(fdf, x="Date", y="Total",  hover_name="Competition", hover_data=["Arr", "EpJ", "PdC", "Série"],
                                      color="Nom", log_x=False, size_max=55,color_discrete_sequence=color_seq, )
        else:
            fig = px.scatter(fdf, x="Date", y="IWF",  hover_name="Competition", hover_data=["Arr", "EpJ", "PdC", "Série"],
                                      color="Nom", log_x=False, size_max=55,color_discrete_sequence=color_seq, )
        fig.update_traces(marker=dict(size=10, symbol='circle'))

        fig.update_xaxes(categoryorder="category ascending", gridcolor='LightGrey')
        fig.update_yaxes(categoryorder="category ascending", gridcolor='LightGrey')
        fig.update_layout(transition_duration=5, plot_bgcolor=plot_col, paper_bgcolor=plot_col,
                          font_color=font_col, font_size=12,
                          title_font_color=font_col, legend_title_font_color=font_col,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.05,
                              xanchor="left",
                              x=-0.05
                            )
                          )
    else:
        fig = px.scatter()
        display_graph = {'display': 'none'}
    return fig, display_graph

# Mise à jour data table
@callback(
    [Output('ag_datatable_athl', 'rowData')],
    [Input('year-slider-athl', 'value'),
     Input('bool_total', 'on'),
     Input('my_txt_input', 'value')
     ])
def update_data_ag(selected_year, on, txt_inserted):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    if txt_inserted:
        fdf = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    else:
        fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if on == True:
        fdf = fdf.sort_values(by=['Total'], ascending=False)
    else:
        fdf = fdf.sort_values(by=['IWF'], ascending=False)
    dat_ag = fdf.to_dict('records')
    return [dat_ag]

# Génération des cartes des 4 premiers athlètes
@callback(
    [Output('athl_card1', 'style'),
     Output("athlete1_nom", "children"),
     Output("athlete1_nom_info", "children"),
     #Output("athlete1_achievements", "children"),
     Output("athlete1_club", "children"),
     Output("athlete1_annivmax", "children"),
     Output('ach_aide-div_athl1', 'style'),
     Output('athl_card2', 'style'),
     Output("athlete2_nom", "children"),
     Output("athlete2_nom_info", "children"),
     #Output("athlete2_achievements", "children"),
     Output("athlete2_club", "children"),
     Output("athlete2_annivmax", "children"),
     Output('ach_aide-div_athl2', 'style'),
     Output('athl_card3', 'style'),
     Output("athlete3_nom", "children"),
     Output("athlete3_nom_info", "children"),
     #Output("athlete3_achievements", "children"),
     Output("athlete3_club", "children"),
     Output("athlete3_annivmax", "children"),
     Output('ach_aide-div_athl3', 'style'),
     Output('athl_card4', 'style'),
     Output("athlete4_nom", "children"),
     Output("athlete4_nom_info", "children"),
     #Output("athlete4_achievements", "children"),
     Output("athlete4_club", "children"),
     Output("athlete4_annivmax", "children"),
     Output('ach_aide-div_athl4', 'style')],
    [Input('year-slider-athl', 'value'),
     Input('my_txt_input', 'value')])

def up_athletes(selected_year, txt_inserted):
    # Perform any manipulation on input_value and return the updated title
    print(txt_inserted)
    up_show = [{'display': 'none'}] * 4
    up_name = [''] * 4
    up_club = [''] * 4
    up_anniv = [''] * 4
    up_date_naiss = [''] * 4
    up_max = [''] * 4
    up_arr = [''] * 4
    up_epj = [''] * 4
    up_total = [''] * 4
    up_pdc = [''] * 4
    up_achievements = [''] * 4
    up_show_ach_aide = [{'display': 'none'}] * 4

    n = 0
    if txt_inserted is None:
        raise PreventUpdate
    for i in txt_inserted:
        up_name[n] = i
        df1 = df[(df['Nom'] == i) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
        df1 = df1.sort_values(by=['Date'], ascending=False)
        if len(df1['Club'].values[0]) > 19:
            up_club[n] = df1['Club'].values[0][0:18] + '.'
        else:
            up_club[n] = df1['Club'].values[0]
        up_show[n] = {'display': 'block'}
        up_anniv[n] = (df1['Né le'].values[0])[-4:]
        up_date_naiss[n] = (df1['Né le'].values[0])
        up_max[n] = str(df1['IWF'].max()) + ' IWF'
        up_arr[n] = str(df1['Arr'].max()) + '/'
        up_epj[n] = str(df1['EpJ'].max()) + '/'
        up_total[n] = df1['Total'].max()
        pdc_df = df1['Total'].idxmax()
        up_pdc[n] = str(df.loc[pdc_df, 'PdC']) + 'kg'
        up_achievements[n] = ''
        if df1['MondeSEN'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['MondeSEN'].values[0]) + ' x 🌎 | '
        if df1['MondeU20'].values[0]+df1['MondeU17'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['MondeU20'].values[0]+df1['MondeU17'].values[0]) + ' x 🌎🐥 | '
        if df1['MondeMasters'].values[0]>0:
            if df1['Sexe'].values[0]=='F':
                up_achievements[n] = up_achievements[n] + str(df1['MondeMasters'].values[0]) + ' x 🌎👵 | '
            else:
                up_achievements[n] = up_achievements[n] + str(df1['MondeMasters'].values[0]) + ' x 🌎👴 | '
        if df1['EuropeSEN'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['EuropeSEN'].values[0]) + ' x 🇪🇺 | '
        if df1['EuropeU23'].values[0]+df1['EuropeU20'].values[0]+df1['EuropeU17'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['EuropeU20'].values[0]+df1['EuropeU17'].values[0]) + ' x 🇪🇺🐥 | '
        if df1['FranceElite'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['FranceElite'].values[0]) + ' x 🇫🇷 | '
        if df1['GrandPrixFederal'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['GrandPrixFederal'].values[0]) + ' x 🐔 | '
        if df1['TropheeNationalU13'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['TropheeNationalU13'].values[0]) + ' x 🇫🇷👶 | '
        if df1['MondeMasters'].values[0]>0:
            if df1['Sexe'].values[0]=='F':
                up_achievements[n] = up_achievements[n] + str(df1['MondeMasters'].values[0]) + ' x 🌎👵 | '
            else:
                up_achievements[n] = up_achievements[n] + str(df1['MondeMasters'].values[0]) + ' x 🌎👴 | '
        if df1['EuropeMasters'].values[0]>0:
            if df1['Sexe'].values[0]=='F':
                up_achievements[n] = up_achievements[n] + str(df1['EuropeMasters'].values[0]) + ' x 🇪🇺👵 | '
            else:
                up_achievements[n] = up_achievements[n] + str(df1['EuropeMasters'].values[0]) + ' x 🇪🇺👴 | '
        if df1['NbCompet'].values[0]==100:
            up_achievements[n] = up_achievements[n] + ' 💯 | '
        if df1['NbCompet'].values[0]==50:
            up_achievements[n] = up_achievements[n] + ' 5️⃣0️⃣ | '
        if df1['Nb6sur6'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['Nb6sur6'].values[0]) + ' x 👌 | '
        if df1['Nb2sur6DerniereBarre'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['Nb2sur6DerniereBarre'].values[0]) + ' x 🫣 | '
        if df1['NbBulles'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['NbBulles'].values[0]) + ' x 🔴 | '
        if df1['NbDoublesBulles'].values[0]>0:
            up_achievements[n] = up_achievements[n] + str(df1['NbDoublesBulles'].values[0]) + ' x 🔴🔴 | '
        if len(up_achievements[n])>0:
            up_achievements[n] = ' - ' + up_achievements[n]
            up_show_ach_aide[n]={'display': 'block'}
        else:
            up_show_ach_aide[n]={'display': 'none'}
        n = n + 1

    return  up_show[0], f"{up_name[0]}", f"{up_name[0]}" + '  ' + f"{up_date_naiss[0]}" + f"{up_achievements[0]}", f"{up_club[0]}", f"{up_anniv[0]}" + ' | PR ' + f"{up_max[0]}", up_show_ach_aide[0], \
            up_show[1], f"{up_name[1]}", f"{up_name[1]}" + '  ' + f"{up_date_naiss[1]}" + f"{up_achievements[1]}", f"{up_club[1]}", f"{up_anniv[1]}" + ' | PR ' + f"{up_max[1]}", up_show_ach_aide[1],  \
            up_show[2], f"{up_name[2]}", f"{up_name[2]}" + '  ' + f"{up_date_naiss[2]}" + f"{up_achievements[2]}", f"{up_club[2]}", f"{up_anniv[2]}" + ' | PR ' + f"{up_max[2]}", up_show_ach_aide[2], \
            up_show[3], f"{up_name[3]}", f"{up_name[3]}" + '  ' + f"{up_date_naiss[3]}" + f"{up_achievements[3]}", f"{up_club[3]}", f"{up_anniv[3]}" + ' | PR ' + f"{up_max[3]}", up_show_ach_aide[3]

# Gestion ouverture +Info Cartes Athlètes
@callback(
    [Output("athl1-modal", "is_open"),
    Output("athl2-modal", "is_open"),
    Output("athl3-modal", "is_open"),
    Output("athl4-modal", "is_open")],
    [Input("open_athl1", "n_clicks"),
    Input("open_athl2", "n_clicks"),
    Input("open_athl3", "n_clicks"),
    Input("open_athl4", "n_clicks"),
    Input("close-athl1", "n_clicks"),
    Input("close-athl2", "n_clicks"),
    Input("close-athl3", "n_clicks"),
    Input("close-athl4", "n_clicks")],
    [State("athl1-modal", "is_open"),
    State("athl2-modal", "is_open"),
    State("athl3-modal", "is_open"),
    State("athl4-modal", "is_open")],
    prevent_initial_call=True
)

# +Info Carte 4
def toggle_modal_athl(open_clicks1, open_clicks2, open_clicks3, open_clicks4, close_clicks1, close_clicks2, close_clicks3, close_clicks4, is_open_athl1, is_open_athl2, is_open_athl3, is_open_athl4):
    if open_clicks1 or close_clicks1:
        is_open_athl1 = not is_open_athl1
        is_open_athl2 = False
        is_open_athl3 = False
        is_open_athl4 = False
    if open_clicks2 or close_clicks2:
        is_open_athl2 = not is_open_athl2
        is_open_athl1 = False
        is_open_athl3 = False
        is_open_athl4 = False
    if open_clicks3 or close_clicks3:
        is_open_athl3 = not is_open_athl3
        is_open_athl1 = False
        is_open_athl2 = False
        is_open_athl4 = False
    if open_clicks4 or close_clicks4:
        is_open_athl4 = not is_open_athl4
        is_open_athl1 = False
        is_open_athl2 = False
        is_open_athl3 = False
    print(str(open_clicks1) + ' ' + str(close_clicks1))
    return is_open_athl1, is_open_athl2, is_open_athl3, is_open_athl4

@callback(
    [Output("athl1-graph", "figure"),
     Output("athl1-graph", "style"),
     Output("athl1-table", "children"),
     Output("athl2-graph", "figure"),
     Output("athl2-graph", "style"),
     Output("athl2-table", "children"),
     Output("athl3-graph", "figure"),
     Output("athl3-graph", "style"),
     Output("athl3-table", "children"),
     Output("athl4-graph", "figure"),
     Output("athl4-graph", "style"),
     Output("athl4-table", "children")],
    [Input('my_txt_input', 'value'),
     Input("athl1-modal", "is_open"),
     Input("athl2-modal", "is_open"),
     Input("athl3-modal", "is_open"),
     Input("athl4-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl4(txt_inserted, is_open_athl1, is_open_athl2, is_open_athl3, is_open_athl4):
    if (not is_open_athl1 and not is_open_athl2 and not is_open_athl3 and not is_open_athl4) or not txt_inserted:
        raise PreventUpdate
    if is_open_athl1:
        athl = txt_inserted[0]
    if is_open_athl2:
        athl = txt_inserted[1]
    if is_open_athl3:
        athl = txt_inserted[2]
    if is_open_athl4:
        athl = txt_inserted[3]
    dirname = os.path.dirname(__file__)
    path_db = os.path.join(dirname, 'dataltero.db')
    conn = sql.connect(database=path_db)
    qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
                    max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
                   , max(round(cat.IWF_Calcul,3)) as "IWF" 
                 FROM ATHLETE as ath 
                 LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                 LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                 LEFT JOIN CLUB as clb on clb.Club = cat.CATClub

                 where ath.Nom='""" + athl + """'
                 group by cmp.SaisonAnnee, clb.club
                 order by cmp.SaisonAnnee asc"""
    df_athl = pd.read_sql_query(qry, conn)
    df_athl.head()

    df2_athl = df2[(df2['Nom'] == athl)]
    df2_athl['Série'] = pd.Categorical(df2_athl['Série'], ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"],
                                        ordered=True)
    df2_athl = df2_athl.sort_values(by=['Série'])
    print(df2_athl)
    fig_athl = px.histogram(df2_athl, x="Série", color="Catégorie",
                             color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple",
                                                      "#54B4D3", "#9FA6B2"],
                             category_orders={
                                 "Série": ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"]})

    fig_athl.update_layout(font_size=12,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.05,
                                xanchor="left",
                                x=-0.05
                            ))
    display_graph_athl = {'display': 'block'}

    if is_open_athl1:
        return fig_athl, display_graph_athl, [dbc.Table.from_dataframe(df_athl, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update,
    if is_open_athl2:
            return dash.no_update, dash.no_update, dash.no_update, fig_athl, display_graph_athl, [dbc.Table.from_dataframe(df_athl, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    if is_open_athl3:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, fig_athl, display_graph_athl, [dbc.Table.from_dataframe(df_athl, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update,
    if is_open_athl4:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, fig_athl, display_graph_athl, [dbc.Table.from_dataframe(df_athl, responsive=True, striped=True, bordered=True, hover=True)]
@callback(
    Output("ag_datatable_athl", "columnDefs"),
    [Input("reset_col", "n_clicks")]
)

def toggle_modal_athl(reset_clicks):
    color_mode = 'color'
    cols = [
                {
                   "headerName": "Athlete",
                   "children": [
                        {"field": "Nom", "width": 200, "pinned": "left", "hide": False},
                        {"field": "PdC", "width": 80, "hide": False},
                        {"field": "Catégorie", "width": 100, "hide": False},
                    ],
                },
                {
                   "headerName": "Arraché",
                   "children": [
                        {"field": "Arr1", "headerName": "1", "width": 60, "hide": False,
                            'cellStyle': {
                                "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                            },
                        },
                        {"field": "Arr2", "headerName": "2", "width": 60, "hide": False,
                            'cellStyle': {
                                "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                            },
                        },
                        {"field": "Arr3", "headerName": "3", "width": 60, "hide": False,
                            'cellStyle': {
                                "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                            },
                        },
                        {"field": "Arr", "width": 75, "hide": False,
                            'cellStyle': {
                                "function": "params.value <=0 ? {" + color_mode + ": 'rgb(235, 61, 85)'} : {" + color_mode + ": 'rgb(59, 113, 202)'}",
                            },
                        },
                    ],
                },
                {
                    "headerName": "Epaulé Jeté", "hide": False,
                        "children": [
                            {"field": "EpJ1", "headerName": "1", "width": 60, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                },
                            },
                            {"field": "EpJ2", "headerName": "2", "width": 60, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                },
                            },
                            {"field": "EpJ3", "headerName": "3", "width": 60, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                },
                            },
                            {"field": "EpJ", "width": 75, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(235, 61, 85)'} : {" + color_mode + ": 'rgb(59, 113, 202)'}",
                                },
                            },
                        ],
                },
                {
                    "headerName": "Performance",
                        "children": [
                            {"field": "Total", "width": 80, "hide": False, "font-weight": 'bold',
                             'cellStyle': {
                                 "function": "params.value <=0 ? {" + color_mode + ": 'rgb(255, 41, 65)'} : {" + color_mode + ": 'rgb(44, 98, 217)'}",
                                },
                             },
                            {"field": "IWF", "width": 80, "hide": False},
                            {"field": "Série", "width": 80, "hide": False},
                        ],
                },
                {
                    "headerName": "Compétition",
                    "children": [
                        {"field": "Date", "width": 150, "hide": False},
                        {"field": "Competition", "hide": False}
                        ],
                }
        ]
    return cols;

@callback(
    [Output("aide_achievements_athl1", "is_open"),
    Output("aide_achievements_athl2", "is_open"),
    Output("aide_achievements_athl3", "is_open"),
    Output("aide_achievements_athl4", "is_open")],
    [Input("open-aide_achievements-athl1", "n_clicks"),
    Input("open-aide_achievements-athl2", "n_clicks"),
    Input("open-aide_achievements-athl3", "n_clicks"),
    Input("open-aide_achievements-athl4", "n_clicks"),
    Input("close-aide_achievements-athl1", "n_clicks"),
    Input("close-aide_achievements-athl2", "n_clicks"),
    Input("close-aide_achievements-athl3", "n_clicks"),
    Input("close-aide_achievements-athl4", "n_clicks")],
    [State("aide_achievements_athl1", "is_open"),
    State("aide_achievements_athl2", "is_open"),
    State("aide_achievements_athl3", "is_open"),
    State("aide_achievements_athl4", "is_open")],
    prevent_initial_call=True
)

# Aide Achievements
def toggle_modal_athl(open_clicks1, open_clicks2, open_clicks3, open_clicks4, close_clicks1, close_clicks2, close_clicks3, close_clicks4, is_open_athl1, is_open_athl2, is_open_athl3, is_open_athl4):
    if open_clicks1 or close_clicks1:
        is_open_athl1 = not is_open_athl1
        is_open_athl2 = False
        is_open_athl3 = False
        is_open_athl4 = False
    if open_clicks2 or close_clicks2:
        is_open_athl2 = not is_open_athl2
        is_open_athl1 = False
        is_open_athl3 = False
        is_open_athl4 = False
    if open_clicks3 or close_clicks3:
        is_open_athl3 = not is_open_athl3
        is_open_athl1 = False
        is_open_athl2 = False
        is_open_athl4 = False
    if open_clicks4 or close_clicks4:
        is_open_athl4 = not is_open_athl4
        is_open_athl1 = False
        is_open_athl2 = False
        is_open_athl3 = False
    print(str(open_clicks1) + ' ' + str(close_clicks1))
    return is_open_athl1, is_open_athl2, is_open_athl3, is_open_athl4

@callback(
    [Output("ach_aide-table_athl1", "children"),
    Output("ach_aide-table_athl2", "children"),
    Output("ach_aide-table_athl3", "children"),
    Output("ach_aide-table_athl4", "children"),
    Output("ach_aide-txt_athl1", "children"),
    Output("ach_aide-txt_athl2", "children"),
    Output("ach_aide-txt_athl3", "children"),
    Output("ach_aide-txt_athl4", "children")],
    [Input("aide_achievements_athl1", "is_open"),
    Input("aide_achievements_athl2", "is_open"),
    Input("aide_achievements_athl3", "is_open"),
    Input("aide_achievements_athl4", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(is_open_ach1, is_open_ach2, is_open_ach3, is_open_ach4):
    if not is_open_ach1 and not is_open_ach2 and not is_open_ach3 and not is_open_ach4:
        raise PreventUpdate
    ach_aide_txt = 'Les symboles affichés à coté de la date de naissance de l''athlète représentent les participations ou performances détaillées dans le tableau ci-dessous : '
    ach = [['🌎', 'Championnats du Monde'], ['🇪🇺', 'Championnats d''Europe'], ['🇫🇷', 'France Elite'], ['🐥', 'Jeunes (U15 à U23)'], ['🇫🇷👶', 'Trophée National U13'], ['👵👴', 'Masters'],
           ['🐔', 'Grand Prix Fédéral'], ['💯', 'Au moins 100 Compétitions'], ['5️⃣0️⃣', 'Au moins 50 Compétitions'], ['👌', '6/6'],
           ['🫣', '2/6 sur les dernières barres des 2 mouvements'], ['🔴', 'Bulle'], ['🔴🔴', 'Double Bulle']]

    # Create the pandas DataFrame
    df_ach = pd.DataFrame(ach, columns=['Symbole', 'Signification'])
    if is_open_ach1:
        return [dbc.Table.from_dataframe(df_ach, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update, ach_aide_txt, dash.no_update, dash.no_update, dash.no_update
    if is_open_ach2:
        return dash.no_update, [dbc.Table.from_dataframe(df_ach, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update, ach_aide_txt,  dash.no_update, dash.no_update
    if is_open_ach3:
        return dash.no_update, dash.no_update, [dbc.Table.from_dataframe(df_ach, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update, ach_aide_txt,  dash.no_update
    if is_open_ach4:
        return dash.no_update, dash.no_update, dash.no_update, [dbc.Table.from_dataframe(df_ach, responsive=True, striped=True, bordered=True, hover=True)], dash.no_update, dash.no_update, dash.no_update, ach_aide_txt

@callback(
    [Output("app_code_athl", "className"),
     Output("ag_datatable_athl", "className"),
     Output("reset_col", "color"),
     Output("bool_total", "label"),
     Output("year-slider-athl", "marks")],
    [Input("bool_light", "on")]
)

def light_mode_athl(on):
    if on == True:
        css_body = "body_light"
        css_grid = "ag-theme-quartz"
        reset_color = "secondary"
        iwf_total_label = {"label": "IWF/Total", 'style': {"color": "rgb(40,40,45)"}}
        slider_marks = {str(year): {'label' : str(year), 'style':{'color':'rgb(40,40,45)'}} for year in df['SaisonAnnee'].unique()}
    else:
        css_body = "body"
        css_grid = "ag-theme-quartz-dark"
        reset_color = "light"
        iwf_total_label = {"label": "IWF/Total", 'style': {"color": "white"}}
        slider_marks = {str(year): {'label' : str(year), 'style':{'color':'white'}} for year in df['SaisonAnnee'].unique()}

    return css_body, css_grid, reset_color, iwf_total_label, slider_marks;

#Export Excel
clientside_callback(
    """async function (n, txt) {
        if (n) {
            grid1Api = await dash_ag_grid.getApiAsync("ag_datatable_athl")
            var spreadsheets = [];
            if (typeof txt[0] === 'undefined') {
                s_name = 'Perfs_Athletes';
                f_name = 'perf_athletes.xlsx'
            } else if (txt.length === 1) {
                s_name = 'Perfs_' + txt[0];
                f_name = 'perf_' + txt[0] + '.xlsx'
            } else {
                s_name = 'Perfs_' + txt[0] + 'et+';
                f_name = 'perf_' + txt[0] + '_et_autres.xlsx'
            }
            spreadsheets.push(
                grid1Api.getSheetDataForExcel({ sheetName: s_name})
            );
            
            grid1Api.exportMultipleSheetsAsExcel({
              data: spreadsheets,
              fileName: f_name,
            });
        }
        return dash_clientside.no_update
    }""",
    Output("excel_export", "n_clicks"),
    Input("excel_export", "n_clicks"),
    State('my_txt_input', 'value'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    run_server(debug=True)