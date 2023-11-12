import dash
import plotly.express as px
from dash import dash_table, dcc, callback, State, html
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
#import numpy as np
import os
from dash.dependencies import Input, Output
#from flask import Flask, render_template
import dash_bootstrap_components as dbc


# Connection à la base SQLite
dirname = os.path.dirname(__file__)
path_db = os.path.join(dirname, 'dataltero.db')
conn = sql.connect(database=path_db)

# Requête principale
qry = """SELECT ath.Nom, ath.DateNaissance as "Né le"
      , substr(cmp."NomCompetitionCourt", 1, 64) as "Competition", cat."PoidsDeCorps" as "PdC", clb.Club
      , cmp.AnneeMois as "Mois", cmp.SaisonAnnee, cmp.MoisCompet, cmp.DateCompet as "Date"
      , cat.Arr1, cat.Arr2, cat.Arr3, cat.Arrache as "Arr", cat.Epj1, cat.Epj2, cat.Epj3, cat.EpJete as "EpJ"
      , cat.Serie as "Série", cat.Categorie as "Catégorie", cat.PoidsTotal as "Total", cat.IWF_Calcul as "IWF" 
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
df['MoisCompet'] = pd.Categorical(df['MoisCompet'],
                                  ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05", "06", "07"])
df2['Série'] = pd.Categorical(df2['Série'],
                                  ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"], ordered=True)


dash.register_page(__name__, path='/')

# Liste d'athlètes = ceux qui ont tiré sur la plage par défaut càd l'année dernière + l'année en cours
selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
list_names = list(set(df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]['Nom'].tolist()))

# body
layout = html.Div([
    # Header & filtres
        dbc.Row([            # Titre
            dbc.Col([
                html.Div(
                    children=[
                        dbc.Button(
                            "  Dashboard Athlètes  ", outline=False, color="danger", className="me-1", href="/club", size="lg"),
                        #dbc.Collapse(
                        #    info_button,
                        #    id="navbar-collapse",
                        #    is_open=False
                        #)
                        ],
                    id='filter_info',
                    className="title-box",
                )], xs=6, sm=6, md=6, lg=2, xl=2),

            # Zone filtres athlètes
            dbc.Col(
                html.Div(
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                options=[x for x in sorted(list_names)],
                                multi=True,
                                id='my_txt_input',
                                placeholder="Choisir des athlètes..."
                                )
                            ],
                            className="input_box1",),
                        #html.Datalist(id='Nom_athl')
                        ])
                ), xs=6, sm=6, md=6, lg=2, xl=2),

            # Cartes athlètes (masquées par défaut)
            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div([html.P("Card 1")], id="athlete1_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete1_club"),
                                    html.Div([html.P("NaissanceMax")], id="athlete1_annivmax")
                                  ],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl1", color="danger", className="mt-auto", size="sm"),
                                dbc.Modal([
                                    dbc.ModalHeader("Information", id="athlete1_nom_info"),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl1-graph', style = {'display': 'none'}),
                                        html.Div(id="athl1-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-athl1", color="secondary", className="ml-auto")
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
                                    dbc.ModalHeader("Information", id="athlete2_nom_info"),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl2-graph', style = {'display': 'none'}),
                                        html.Div(id="athl2-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-athl2", color="secondary", className="ml-auto")
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
                                    dbc.ModalHeader("Information", id="athlete3_nom_info"),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl3-graph', style = {'display': 'none'}),
                                        html.Div(id="athl3-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-athl3", color="secondary", className="ml-auto")
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
                                    dbc.ModalHeader("Information", id="athlete4_nom_info"),
                                    dbc.ModalBody([
                                        dcc.Graph(id='athl4-graph', style = {'display': 'none'}),
                                        html.Div(id="athl4-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Close", id="close-athl4", color="secondary", className="ml-auto")
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
            html.Div([
                dcc.Graph(
                    id='graph-with-slider',
                    style= {'display': 'none'}
                ),
                dcc.RangeSlider(
                    df['SaisonAnnee'].min(),
                    df['SaisonAnnee'].max(),
                    step=None,
                    value=selected_year,
                    marks={str(year): str(year) for year in df['SaisonAnnee'].unique()},
                    id='year-slider',
                    className='slider_zone')],
                id='div_output',
                className='graph_box'
            ),
        ], width=12),
    ]),

    # Zone data table
    html.Br(),
    html.Div([
        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id='datatable-interactivity',
                    # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
                    columns=[
                        {"name": i, "id": i, "selectable": True} for i in
                            ['Nom',  'Date', 'PdC', 'Arr1', 'Arr2', 'Arr3', 'Arr', 'EpJ1', 'EpJ2', 'EpJ3', 'EpJ', 'Total', 'IWF', 'Série', 'Catégorie', 'Competition']
                    ],
                    data=df.to_dict('records'),
                    editable=False,
                    fixed_rows={'headers': True},
                    sort_action="native",
                    sort_mode="single",
                    virtualization=True,
                    style_table={
                        'overflowX': 'scroll'
                    },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'text-align': 'left',
                        'text-indent': '0.2em'
                    },
                    style_data={
                        'backgroundColor': 'dimgray',
                        'color': 'white',
                        'border': '1px solid white'
                    },
                    style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'minWidth': '40px',
                        'maxWidth': '200px'
                    },
                    # Mise en forme conditionelle pour les bulles
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{Arr1} <= 0',
                                'column_id': 'Arr1'
                            },
                            'backgroundColor': 'rgb(220, 76, 100)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr1} > 0',
                                'column_id': 'Arr1'
                            },
                            'backgroundColor': 'rgb(20, 164, 77)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr2} <= 0',
                                'column_id': 'Arr2'
                            },
                            'backgroundColor': 'rgb(220, 76, 100)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr2} > 0',
                                'column_id': 'Arr2'
                            },
                            'backgroundColor': 'rgb(20, 164, 77)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr3} <= 0',
                                'column_id': 'Arr3'
                            },
                            'backgroundColor': 'rgb(220, 76, 100)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr3} > 0',
                                'column_id': 'Arr3'
                            },
                            'backgroundColor': 'rgb(20, 164, 77)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr} <= 0',
                                'column_id': 'Arr'
                            },
                            'backgroundColor': 'darkred',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{Arr} > 0',
                                'column_id': 'Arr'
                            },
                            'backgroundColor': 'rgb(59, 113, 202)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ1} <=0',
                                'column_id': 'EpJ1'
                            },
                            'backgroundColor': 'rgb(220, 76, 100)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ1} >0',
                                'column_id': 'EpJ1'
                            },
                            'backgroundColor': 'rgb(20, 164, 77)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ2} <=0',
                                'column_id': 'EpJ2'
                            },
                            'backgroundColor': 'rgb(220, 76, 100)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ2} >0',
                                'column_id': 'EpJ2'
                            },
                            'backgroundColor': 'rgb(20, 164, 77)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ3} <=0',
                                'column_id': 'EpJ3'
                            },
                            'backgroundColor': 'rgb(220, 76, 100)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ3} >0',
                                'column_id': 'EpJ3'
                            },
                            'backgroundColor': 'rgb(20, 164, 77)',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ} <= 0',
                                'column_id': 'EpJ'
                            },
                            'backgroundColor': 'darkred',
                            'color': 'white'
                        },
                        {
                            'if': {
                                'filter_query': '{EpJ} > 0',
                                'column_id': 'EpJ'
                            },
                            'backgroundColor': 'rgb(59, 113, 202)',
                            'color': 'white'
                        },
                    ],
                    row_selectable=False,
                    row_deletable=False,
                    selected_columns=[],
                    selected_rows=[],
                    style_as_list_view=True,
                    page_action="native",
                    page_current=0,
                    page_size=25)
            ], width=12),
        ]),
    ], className='data_tab'),
    html.Link(
        rel='stylesheet',
        href='/assets/01_dash_board.css'
    )
],
    id='app_code',
    className='body'
)

# Mise à jour de la liste d'athlète dispo en fonction des années de référence
@callback(
    Output('my_txt_input', 'options'),
    Input('year-slider', 'value'),
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
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])
def update_figure(selected_year, txt_inserted):
    if selected_year == '':
        selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
    fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if txt_inserted:
        # On trie par nom pour aligner la saisie, les cartes et le graphique
        fdf = fdf[(fdf['Nom'].isin(txt_inserted))]
        fdf.Nom = fdf.Nom.astype("category")
        fdf.Nom = fdf.Nom.cat.set_categories(txt_inserted)
        fdf = fdf.sort_values(by='Nom')
        display_graph = {'display': 'block'}

        #Paramètres de graph
        fig = px.scatter(fdf, x="Mois", y="IWF", hover_name="Competition", hover_data=["Arr", "EpJ", "PdC", "Série"],
                                      color="Nom", log_x=False, size_max=55,color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"], )
        fig.update_traces(marker=dict(size=10, symbol='circle') )
        fig.update_xaxes(categoryorder="category ascending")
        fig.update_yaxes(categoryorder="category ascending")
        fig.update_layout(transition_duration=5, plot_bgcolor='rgb(40,40,45)', paper_bgcolor='rgb(40,40,45)',
                          font_color="white", font_size=12,
                          title_font_color="white", legend_title_font_color="white",
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
    [Output('datatable-interactivity', "data"),
     Output('datatable-interactivity', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])

def update_data(selected_year, txt_inserted):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    if txt_inserted:
        fdf = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    else:
        fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

    columns = [
             {"name": i, "id": i, "selectable": True} for i in
             ['Nom',  'Date', 'PdC', 'Arr1', 'Arr2', 'Arr3', 'Arr', 'EpJ1', 'EpJ2', 'EpJ3', 'EpJ', 'Total', 'IWF', 'Série', 'Catégorie', 'Competition']
     ]

    fdf = fdf.sort_values(by=['IWF'], ascending=False)
    dat = fdf.to_dict('records')

    return dat, columns

# Génération des cartes des 4 premiers athlètes
@callback(
    [Output('athl_card1', 'style'),
     Output("athlete1_nom", "children"),
     Output("athlete1_nom_info", "children"),
     Output("athlete1_club", "children"),
     Output("athlete1_annivmax", "children"),
     Output('athl_card2', 'style'),
     Output("athlete2_nom", "children"),
     Output("athlete2_nom_info", "children"),
     Output("athlete2_club", "children"),
     Output("athlete2_annivmax", "children"),
     Output('athl_card3', 'style'),
     Output("athlete3_nom", "children"),
     Output("athlete3_nom_info", "children"),
     Output("athlete3_club", "children"),
     Output("athlete3_annivmax", "children"),
     Output('athl_card4', 'style'),
     Output("athlete4_nom", "children"),
     Output("athlete4_nom_info", "children"),
     Output("athlete4_club", "children"),
     Output("athlete4_annivmax", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])

def updated_athletes(selected_year, txt_inserted):
    # Perform any manipulation on input_value and return the updated title
    updated_show = [{'display': 'none'}] * 4
    updated_name = [''] * 4
    updated_club = [''] * 4
    updated_anniv = [''] * 4
    updated_date_naiss = [''] * 4
    updated_max = [''] * 4
    updated_arr = [''] * 4
    updated_epj = [''] * 4
    updated_total = [''] * 4
    updated_pdc = [''] * 4

    n = 0
    if txt_inserted is None:
        raise PreventUpdate
    for i in txt_inserted:
        updated_name[n] = i
        df1 = df[(df['Nom'] == i) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
        df1 = df1.sort_values(by=['Date'], ascending=False)
        if len(df1['Club'].values[0]) > 19:
            updated_club[n] = df1['Club'].values[0][0:18] + '.'
        else:
            updated_club[n] = df1['Club'].values[0]
        updated_show[n] = {'display': 'block'}
        updated_anniv[n] = (df1['Né le'].values[0])[-4:]
        updated_date_naiss[n] = (df1['Né le'].values[0])
        updated_max[n] = str(df1['IWF'].max()) + ' IWF'
        updated_arr[n] = str(df1['Arr'].max()) + '/'
        updated_epj[n] = str(df1['EpJ'].max()) + '/'
        updated_total[n] = df1['Total'].max()
        pdc_df = df1['Total'].idxmax()
        updated_pdc[n] = str(df.loc[pdc_df, 'PdC']) + 'kg'
        n = n + 1

    return updated_show[0], f"{updated_name[0]}", f"{updated_name[0]}" + ' ' + f"{updated_date_naiss[0]}", f"{updated_club[0]}", f"{updated_anniv[0]}" + ' | PR ' + f"{updated_max[0]}",\
        updated_show[1], f"{updated_name[1]}", f"{updated_name[1]}" + ' ' + f"{updated_date_naiss[1]}",f"{updated_club[1]}", f"{updated_anniv[1]}"+ ' | PR ' + f"{updated_max[1]}",  \
        updated_show[2], f"{updated_name[2]}", f"{updated_name[2]}" + ' ' + f"{updated_date_naiss[2]}",f"{updated_club[2]}", f"{updated_anniv[2]}"+ ' | PR ' + f"{updated_max[2]}", \
        updated_show[3], f"{updated_name[3]}", f"{updated_name[3]}" + ' ' + f"{updated_date_naiss[3]}", f"{updated_club[3]}", f"{updated_anniv[3]}"+ ' | PR ' + f"{updated_max[3]}" #f"{updated_arr[3]}{updated_epj[3]}{updated_total[3]}", f"{updated_pdc[3]}",

# Gestion ouverture +Info Carte 1
@callback(
    Output("athl1-modal", "is_open"),
    [Input("open_athl1", "n_clicks"),
    Input("close-athl1", "n_clicks")],
    State("athl1-modal", "is_open"),
    prevent_initial_call=True
)

def toggle_modal_athl(open_clicks, close_clicks, is_open_athl1):
    if open_clicks or close_clicks:
        return not is_open_athl1
    return is_open_athl1

# +Info Carte 1
@callback(
    [Output("athl1-graph", "figure"),
     Output("athl1-graph", "style"),
     Output("athl1-table", "children")],
    [Input(component_id='my_txt_input', component_property='value'),
     Input("athl1-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(txt_inserted, is_open_athl1):
    if not is_open_athl1 or not txt_inserted:
        raise PreventUpdate
    if is_open_athl1:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        athl1 = txt_inserted[0]
        qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
                 max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
                , max(round(cat.IWF_Calcul,3)) as "IWF" 
              FROM ATHLETE as ath 
              LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
              LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
              LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
              
              where ath.Nom='""" + athl1 + """'
              group by cmp.SaisonAnnee, clb.club
              order by cmp.SaisonAnnee asc"""
        df_athl1 = pd.read_sql_query(qry, conn)
        df_athl1.head()

        df2_athl1 = df2[(df2['Nom'] == txt_inserted[0])]
        df2_athl1['Série'] = pd.Categorical(df2_athl1['Série'],
                                      ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"],
                                      ordered=True)
        df2_athl1 = df2_athl1.sort_values(by=['Série'])
        print(df2_athl1)

        fig_athl1 = px.histogram(df2_athl1, x="Série", color="Catégorie",
                                 color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"],
                                 category_orders={"Série":["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"]})

        fig_athl1.update_layout(font_size=12,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.05,
                              xanchor="left",
                              x=-0.05
                          ))
        display_graph_athl1 = {'display': 'block'}

        return fig_athl1, display_graph_athl1, [dbc.Table.from_dataframe(df_athl1, responsive = True, striped=True, bordered=True, hover=True)]

# Gestion ouverture +Info Carte 2
@callback(
    Output("athl2-modal", "is_open"),
    [Input("open_athl2", "n_clicks"),
    Input("close-athl2", "n_clicks")],
    State("athl2-modal", "is_open"),
    prevent_initial_call=True
)

def toggle_modal_athl(open_clicks, close_clicks, is_open_athl2):
    if open_clicks or close_clicks:
        return not is_open_athl2
    return is_open_athl2

# +Info Carte 2
@callback(
    [Output("athl2-graph", "figure"),
     Output("athl2-graph", "style"),
     Output("athl2-table", "children")],
    [Input(component_id='my_txt_input', component_property='value'),
     Input("athl2-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl2(txt_inserted, is_open_athl2):
    if not is_open_athl2 or not txt_inserted:
        raise PreventUpdate
    if is_open_athl2:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        athl2 = txt_inserted[1]
        qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
                 max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
                , max(round(cat.IWF_Calcul,3)) as "IWF" 
              FROM ATHLETE as ath 
              LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
              LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
              LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
              
              where ath.Nom='""" + athl2 + """'
              group by cmp.SaisonAnnee, clb.club
              order by cmp.SaisonAnnee asc"""
        df_athl2 = pd.read_sql_query(qry, conn)
        df_athl2.head()

        df2_athl2 = df2[(df2['Nom'] == txt_inserted[1])]
        df2_athl2 = df2_athl2.sort_values(by=['Série'])
        print(df2_athl2)

        fig_athl2 = px.histogram(df2_athl2, x="Série", color="Catégorie", color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"])
        #fig_athl2.update_xaxes(categoryorder="category ascending")

        fig_athl2.update_xaxes(categoryorder="category ascending")
        fig_athl2.update_layout(font_size=12,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.05,
                              xanchor="left",
                              x=-0.05
                          ))
        display_graph_athl2 = {'display': 'block'}

        return fig_athl2, display_graph_athl2, [dbc.Table.from_dataframe(df_athl2, responsive = True, striped=True, bordered=True, hover=True)]

# Gestion ouverture +Info Carte 3
@callback(
    Output("athl3-modal", "is_open"),
    [Input("open_athl3", "n_clicks"),
    Input("close-athl3", "n_clicks")],
    State("athl3-modal", "is_open"),
    prevent_initial_call=True
)

def toggle_modal_athl(open_clicks, close_clicks, is_open_athl3):
    if open_clicks or close_clicks:
        return not is_open_athl3
    return is_open_athl3

# +Info Carte 3
@callback(
    [Output("athl3-graph", "figure"),
     Output("athl3-graph", "style"),
     Output("athl3-table", "children")],
    [Input(component_id='my_txt_input', component_property='value'),
     Input("athl3-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl3(txt_inserted, is_open_athl3):
    if not is_open_athl3 or not txt_inserted:
        raise PreventUpdate
    if is_open_athl3:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        athl3 = txt_inserted[2]
        qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
                 max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
                , max(round(cat.IWF_Calcul,3)) as "IWF" 
              FROM ATHLETE as ath 
              LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
              LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
              LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
              
              where ath.Nom='""" + athl3 + """'
              group by cmp.SaisonAnnee, clb.club
              order by cmp.SaisonAnnee asc"""
        df_athl3 = pd.read_sql_query(qry, conn)
        df_athl3.head()

        df2_athl3 = df2[(df2['Nom'] == txt_inserted[2])]
        df2_athl3 = df2_athl3.sort_values(by=['Série'])
        print(df2_athl3)

        fig_athl3 = px.histogram(df2_athl3, x="Série", color="Catégorie", color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"])
        #fig_athl3.update_xaxes(categoryorder="category ascending")
        fig_athl3.update_layout(font_size=12,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.05,
                              xanchor="left",
                              x=-0.05
                          ))
        display_graph_athl3 = {'display': 'block'}

        return fig_athl3, display_graph_athl3, [dbc.Table.from_dataframe(df_athl3, responsive = True, striped=True, bordered=True, hover=True)]

# Gestion ouverture +Info Carte 4
@callback(
    Output("athl4-modal", "is_open"),
    [Input("open_athl4", "n_clicks"),
    Input("close-athl4", "n_clicks")],
    State("athl4-modal", "is_open"),
    prevent_initial_call=True
)

# +Info Carte 4
def toggle_modal_athl(open_clicks, close_clicks, is_open_athl4):
    if open_clicks or close_clicks:
        return not is_open_athl4
    return is_open_athl4

@callback(
    [Output("athl4-graph", "figure"),
     Output("athl4-graph", "style"),
     Output("athl4-table", "children")],
    [Input(component_id='my_txt_input', component_property='value'),
     Input("athl4-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl4(txt_inserted, is_open_athl4):
    if not is_open_athl4 or not txt_inserted:
        raise PreventUpdate
    if is_open_athl4:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        athl4 = txt_inserted[3]
        qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
                 max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
                , max(round(cat.IWF_Calcul,3)) as "IWF" 
              FROM ATHLETE as ath 
              LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
              LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
              LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
              
              where ath.Nom='""" + athl4 + """'
              group by cmp.SaisonAnnee, clb.club
              order by cmp.SaisonAnnee asc"""
        df_athl4 = pd.read_sql_query(qry, conn)
        df_athl4.head()

        df2_athl4 = df2[(df2['Nom'] == txt_inserted[3])]
        df2_athl4 = df2_athl4.sort_values(by=['Série'])
        print(df2_athl4)

        fig_athl4 = px.histogram(df2_athl4, x="Série", color="Catégorie", color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"])
        #fig_athl4.update_xaxes(categoryorder="category ascending")

        fig_athl4.update_layout(font_size=12,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.05,
                              xanchor="left",
                              x=-0.05
                          ))
        display_graph_athl4 = {'display': 'block'}

        return fig_athl4, display_graph_athl4, [dbc.Table.from_dataframe(df_athl4, responsive = True, striped=True, bordered=True, hover=True)]



if __name__ == '__main__':
    run_server(debug=True)

