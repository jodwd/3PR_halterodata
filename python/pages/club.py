import dash
import plotly.express as px
from dash import dash_table, dcc, callback, State, html
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
                ath.Nom             as "Nom"
            ,   clb.Club            as "Club"
            ,   clb.Ligue           as "Ligue"
            ,   cat."Sexe"          as "Sexe"
            ,   cat.Arrache         as "Arr"
            ,   cat.ArracheU13      as "ArrU13"
            ,   cat.EpJete          as "EpJ"
            ,   cat.EpJeteU13       as "EpJU13"
            ,   cat.PoidsTotal      as "Tot"
            ,   cat.PoidsDeCorps    as "PdC"
            ,   cat.IWF_Calcul      as "IWF"   
            ,   apr.SaisonAnnee     as "SaisonAnnee"
            ,   apr.MaxIWFSaison    as "Max IWF"
            ,   cat.Serie           as "Serie"
            ,   cat.RangSerie       as "RangSerie"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee" order by cat.IWF_Calcul desc) as "RowNum"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee", cat.CatePoids
                                  order by cat.PoidsTotal desc) as "RowNumMaxCateTotal"
          FROM ATHLETE as ath 
          LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
          LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
          LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
          LEFT JOIN ATHLETE_PR as apr on apr.AthleteID = ath.AthleteID and apr.SaisonAnnee = cmp.SaisonAnnee)
      """

df = pd.read_sql_query(qry, conn)
df.head()

df['IWF'] = round(df['IWF'], 3)
df['Max IWF'] = round(df['Max IWF'], 3)

dfh = df
dff = df
dfh['Rang'] = df[(df['Sexe'] == 'M') & df['SaisonAnnee'] == max(df['SaisonAnnee'])].groupby(['SaisonAnnee']).cumcount() + 1
dff['Rang'] = df[(df['Sexe'] == 'F') & df['SaisonAnnee'] == max(df['SaisonAnnee'])].groupby(['SaisonAnnee']).cumcount() + 1

updated_title='Dashboard Club'

#app = dash.Dash(__name__)
dash.register_page(__name__, name='3PR - Clubs', title='3PR - Dashboard Clubs', image='/assets/3PR.png', description='Tableau de bord des performances des clubs d''haltérophilie français')
#server = server


#df_unique_names = df['Nom'].unique  # Fetch or generate data from Python
df = df.sort_values(by=['RangSerie'])
nom_ligue = list(set(df['Ligue'].tolist()))
nom_club = list(set(df['Club'].tolist()))
nom_serie = df['Serie'].unique().tolist()

#body
layout = html.Div([
    #Header & filtres
    dbc.Row([
        dbc.Col([
            html.Div(
                children=[
                    dbc.Button(
                        "  Dashboard Clubs  ", outline=False, color="primary", className="me-1", href="/club", size="lg"),
                    # dbc.Collapse(
                    #    info_button,
                    #    id="navbar-collapse",
                    #    is_open=False
                    # )
                ],
                id='filter_info',
                className="title-box",
            )], xs=6, sm=6, md=6, lg=2, xl=2),

            # Zone filtres Ligue / Club
            dbc.Col([
                dcc.Dropdown(
                    options=[x for x in sorted(nom_ligue)],
                    multi=True,
                    id='txt-ligue',
                    placeholder="Ligue",
                    className="input-box",
                )
            ],  xs=6, sm=6, md=6, lg=3, xl=3),
            dbc.Col([
                dcc.Dropdown(
                    options=[x for x in sorted(nom_club)],
                    multi=True,
                    id='txt-club',
                    placeholder="Club",
                    className="input-box",
                )
            ], xs=6, sm=6, md=6, lg=3, xl=3),
            dbc.Col([
                dcc.Dropdown(
                    options=[x for x in nom_serie],
                    multi=True,
                    id='txt-serie',
                    placeholder="Série",
                    className="input-box",
                )
            ], xs=6, sm=6, md=6, lg=3, xl=3),
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


    # Nombre athlètes par catégorie
    dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div([html.P("U10/U13")], id="u10_u13_card", className="card-title"),
                            html.Div([
                                html.Div([html.P("Nb Athl")], id="u10_u13_nb_athl"),
                                html.Div([html.P("Nb Comp")], id="u10_u13_nb_comp")
                            ], className="card-text",
                            ),
                            dbc.Button("+ Info", id="open_u10_u13", color="danger", className="mt-auto", size="sm"),
                            dbc.Modal([
                                dbc.ModalHeader("Classement des Athlètes U10 & U13", id="u10_u13_info"),
                                dbc.ModalBody([
                                    dcc.Graph(id='u10_u13-graph', style={'display': 'none'}),
                                    html.Div(id="u10_u13-table", className="athl_data_tab"),
                                ]),
                                dbc.ModalFooter(
                                    dbc.Button("Fermer", id="close-u10_u13", color="secondary", className="ml-auto")
                                ),
                            ], id="u10_u13-modal", size="lg", centered=True, is_open=False),
                        ]
                    ),
                ),
            ], id="cateage_card1", style={'display': 'none'}),
        ], xs=6, sm=3, md=3, lg=2, xl=2),

        dbc.Col([
            html.Div([
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div([html.P("U15/U17")], id="u15_u17_card", className="card-title"),
                            html.Div([
                                html.Div([html.P("Nb Athl")], id="u15_u17_nb_athl"),
                                html.Div([html.P("Nb Comp")], id="u15_u17_nb_comp")
                            ], className="card-text",
                            ),
                            dbc.Button("+ Info", id="open_u15_u17", color="primary", className="mt-auto", size="sm"),
                            dbc.Modal([
                                dbc.ModalHeader("Classement des Athlètes U15 & U17", id="u15_u17_info"),
                                dbc.ModalBody([
                                    dcc.Graph(id='u15_u17-graph', style={'display': 'none'}),
                                    html.Div(id="u15_u17-table", className="athl_data_tab"),
                                ]),
                                dbc.ModalFooter(
                                    dbc.Button("Fermer", id="close-u15_u17", color="secondary", className="ml-auto")
                                ),
                            ], id="u15_u17-modal", size="lg", centered=True, is_open=False),
                        ]
                    ),
                ),
            ], id="cateage_card2", style={'display': 'none'}),
        ], xs=6, sm=3, md=3, lg=2, xl=2),

        dbc.Col([
            html.Div([
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div([html.P("U20")], id="u20_card", className="card-title"),
                            html.Div([
                                html.Div([html.P("Nb Athl")], id="u20_nb_athl"),
                                html.Div([html.P("Nb Comp")], id="u20_nb_comp")
                            ], className="card-text",
                            ),
                            dbc.Button("+ Info", id="open_u20", color="warning", className="mt-auto", size="sm"),
                            dbc.Modal([
                                dbc.ModalHeader("Classement des Athlètes U20", id="u20_info"),
                                dbc.ModalBody([
                                    dcc.Graph(id='u20-graph', style={'display': 'none'}),
                                    html.Div(id="u20-table", className="athl_data_tab"),
                                ]),
                                dbc.ModalFooter(
                                    dbc.Button("Fermer", id="close-u20", color="secondary", className="ml-auto")
                                ),
                            ], id="u20-modal", size="lg", centered=True, is_open=False),
                        ]
                    ),
                ),
            ], id="cateage_card3", style={'display': 'none'}),
        ], xs=6, sm=3, md=3, lg=2, xl=2),

        dbc.Col([
            html.Div([
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div([html.P("SEN")], id="sen_card", className="card-title"),
                            html.Div([
                                html.Div([html.P("Nb Athl")], id="sen_nb_athl"),
                                html.Div([html.P("Nb Comp")], id="sen_nb_comp")
                            ], className="card-text",
                            ),
                            dbc.Button("+ Info", id="open_sen", color="success", className="mt-auto", size="sm"),
                            dbc.Modal([
                                dbc.ModalHeader("Classement des Athlètes Seniors", id="sen_info"),
                                dbc.ModalBody([
                                    dcc.Graph(id='sen-graph', style={'display': 'none'}),
                                    html.Div(id="sen-table", className="athl_data_tab"),
                                ]),
                                dbc.ModalFooter(
                                    dbc.Button("Fermer", id="close-sen", color="secondary", className="ml-auto")
                                ),
                            ], id="sen-modal", size="lg", centered=True, is_open=False),
                        ]
                    ),
                ),
            ], id="cateage_card4", style={'display': 'none'}),
        ], xs=6, sm=3, md=3, lg=2, xl=2),
    ],  className="top_zone",),

    html.Br(),

    #top 5 H & F
    dbc.Row([
        dbc.Col([
            dbc.Button(
                title="  Top 5 Hommes  ", id="top_5_h", outline=True, color="primary", className="me-1", href="/club", size="md"),
            dash_table.DataTable(
                id='datatable-h',
                # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
                columns=[
                    {"name": i, "id": i, "selectable": True} for i in
                    ['Rang', 'Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'Max IWF']
                ],
                data=dfh.to_dict('records'),
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
                    'font-size': '14px',
                    'text-indent': '0.2em'
                },
                style_data={
                    'backgroundColor': 'rgb(80, 80, 90)',
                    'color': 'white',
                    'font-size': '14px',
                    'font-family': 'sans-serif',
                    'border': '1px solid white'
                },
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'minWidth': '40px',
                    'maxWidth': '200px'
                },
                style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'dimgray',
                        }
                ],
                row_selectable=False,
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                style_as_list_view=True,
                page_action="native",
                page_current=0,
                page_size=25),
            ], xs=12, sm=12, md=6, lg=6, xl=6),


        dbc.Col([
            dbc.Button(
                title="  Top 5 Femmes  ", id="top_5_f", outline=True, color="primary", className="me-1", href="/club", size="md"),

            dash_table.DataTable(
                id='datatable-f',
                # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
                columns=[
                    {"name": i, "id": i, "selectable": True} for i in
                    ['Rang', 'Nom', 'Arr', 'EpJ', 'Total', 'Serie', 'PdC', 'Max IWF']
                ],
                data=dff.to_dict('records'),
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
                    'font-size': '14px',
                    'text-indent': '0.2em'
                },
                style_data={
                    'backgroundColor': 'rgb(80, 80, 90)',
                    'color': 'white',
                    'font-family': 'sans-serif',
                    'font-size': '14px',
                    'border': '1px solid white'
                },
                style_cell={
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'minWidth': '40px',
                    'maxWidth': '200px'
                },
                style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'dimgray',
                        }
                ],
                row_selectable=False,
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                style_as_list_view=True,
                page_action="native",
                page_current=0,
                page_size=25,
            ),
        ] , xs=12, sm=12, md=6, lg=6, xl=6),
    ]),



    html.Div([
    ], className='data_tabs'),
    html.Div(id='datatable-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/02_club.css'
        ),
    html.Div(id='none', children=[], style={'display': 'none'})
    ],
    id='app_code',
    className='body'
)

@callback(
    Output('txt-club', 'options'),
    [Input('year-slider', 'value'),
     Input('txt-ligue', 'value')]
)

def update_datalist(selected_year, txt_ligue1):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_ligue1:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_ligue1))]

    nom_club = list(set(filtered_df['Club'].tolist()))
    print(nom_club)
    opt = [x for x in sorted(nom_club)]
    return opt

@callback(
    [Output("top_5_h", "children"),
     Output('datatable-h', "data"),
     Output('datatable-h', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value'),
     Input(component_id='txt-serie', component_property='value')
     ])

def update_data(selected_year=None, txt_ligue=None, txt_club=None, txt_serie=None):
    global updated_title_h
    fdfh = df[(df['Sexe'] == 'M')]
    if selected_year == '':
        selected_year = fdfh['SaisonAnnee'].max()
    if not txt_serie:
        fdfh = fdfh[(fdfh['RowNum'] == 1)]
    else:
        fdfh = fdfh[(fdfh['RowNumMaxCateTotal'] == 1) & (fdfh['Serie'].isin(txt_serie))]
    if txt_ligue or txt_club:
        if txt_ligue:
            fdfh = fdfh[(fdfh['Ligue'].isin(txt_ligue)) & (fdfh['SaisonAnnee'] == selected_year)]
        if txt_club:
            fdfh = fdfh[(fdfh['Club'].isin(txt_club)) & (fdfh['SaisonAnnee'] == selected_year)]
    else:
        fdfh = fdfh[(fdfh['SaisonAnnee'] == selected_year)]

    fdfh=fdfh.sort_values(by=['Max IWF'], ascending=False)
    fdfh['Rang'] = fdfh.groupby(['SaisonAnnee']).cumcount()+1
    columns = [
            {"name": i, "id": i,  "selectable": True} for i in
            ['Rang', 'Nom', 'Arr', 'EpJ', 'Tot', 'Serie', 'PdC', 'IWF']
    ]

    dat = fdfh.to_dict('records')

    #Top 5
    filtered_df=round(fdfh.head(5),0)
    res = filtered_df['Max IWF'].sum()
    updated_title_h = "Top 5 Hommes : " + str(int(res))

    return updated_title_h, dat, columns

@callback(
    [Output("top_5_f", "children"),
     Output('datatable-f', "data"),
     Output('datatable-f', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value'),
     Input(component_id='txt-serie', component_property='value')
     ])

def update_data(selected_year=None, txt_ligue=None, txt_club=None, txt_serie=None):
    global updated_title_f
    fdff = df[(df['Sexe'] == 'F')]
    if selected_year == '':
        selected_year = fdff['SaisonAnnee'].max()
    if not txt_serie:
        fdff = fdff[(fdff['RowNum'] == 1)]
    else:
        fdff = fdff[(fdff['RowNumMaxCateTotal'] == 1) & (fdff['Serie'].isin(txt_serie))]
    if txt_ligue or txt_club:
        if txt_ligue:
            fdff = fdff[(fdff['Ligue'].isin(txt_ligue)) & (fdff['SaisonAnnee'] == selected_year)]
        if txt_club:
            fdff = fdff[(fdff['Club'].isin(txt_club)) & (fdff['SaisonAnnee'] == selected_year)]
    else:
        fdff = fdff[(fdff['SaisonAnnee'] == selected_year)]

    fdff=fdff.sort_values(by=['Max IWF'], ascending=False)
    fdff['Rang'] = fdff.groupby(['SaisonAnnee']).cumcount()+1

    columns = [
            {"name": i, "id": i,  "selectable": True} for i in
            ['Rang', 'Nom', 'Arr', 'EpJ', 'Tot', 'Serie', 'PdC', 'IWF']
    ]

    dat = fdff.to_dict('records')

    filtered_df=round(fdff.head(4),0)
    res = filtered_df['Max IWF'].sum()
    updated_title_f = "Top 4 Femmes : " + str(int(res))

    return updated_title_f, dat, columns



# @callback(
#     [Input('year-slider', 'value'),
#      Input(component_id='txt-ligue', component_property='value'),
#      Input(component_id='txt-club', component_property='value')
#      ])
#
# def update_title(selected_year, txt_ligue, txt_club):
#     # Perform any manipulation on input_value and return the updated title
#     global updated_title_f
#     fdff = df[(df['Sexe'] == 'F')]
#     if selected_year == '':
#         selected_year = fdff['SaisonAnnee'].max()
#     if txt_serie:
#     if txt_ligue or txt_club:
#         if txt_ligue:
#             fdff = fdff[
#                 (fdff['Ligue'].isin(txt_ligue)) & (fdff['SaisonAnnee'] == selected_year)]
#         if txt_club:
#             fdff = fdff[
#                 (fdff['Club'].isin(txt_club)) & (fdff['SaisonAnnee'] == selected_year)]
#     else:
#         fdff = fdff[(fdff['SaisonAnnee'] == selected_year)]
#
#     fdff = fdff.sort_values(by=['Max IWF'], ascending=False)
#
#     return updated_title_f

# Mise à jour des cartes par catégorie d'age
# Nb athletes (classement) / nb participations (Classement part)

@callback(
    [Output('cateage_card1', 'style'),
     Output("u10_u13_nb_athl", "children"),
     Output("u10_u13_nb_comp", "children"),
     Output('cateage_card2', 'style'),
     Output("u15_u17_nb_athl", "children"),
     Output("u15_u17_nb_comp", "children"),
     Output('cateage_card3', 'style'),
     Output("u20_nb_athl", "children"),
     Output("u20_nb_comp", "children"),
     Output('cateage_card4', 'style'),
     Output("sen_nb_athl", "children"),
     Output("sen_nb_comp", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value')
     ])

def updated_athletes(selected_year, txt_ligue, txt_club):

    print(txt_club)

    # card display management (by 'ligue' or by 'club' and only if one ligue or club chosen)
    txt_qry = 'clb.club'
    mode_ligue = False
    disp_cards = False
    if txt_ligue and not txt_club:
        mode_ligue = True
        txt_qry='clb.ligue'
        if len(txt_ligue) == 1:
            disp_cards = True
    if txt_club:
        if len(txt_club) == 1:
            disp_cards = True

    conn = sql.connect(database=path_db)
    qry_age = """SELECT
    cmp.SaisonAnnee             as "Saison",""" + txt_qry + """,
    CASE
        WHEN cat."CateAge" IN ('U10','U13') THEN 'U10/U13'
        WHEN cat."CateAge" IN ('U15','U17') THEN 'U15/U17'
        WHEN cat."CateAge" = 'U20' THEN 'U20'
        ELSE 'SEN'
    END                          as "CateAge",
    rclb.row_num_nb_part         as "RangPartClubCateAge",
    rclb.row_num_nb_athl         as "RangAthlClubCateAge",
    COUNT(1)                     as "NbPart",
    COUNT(DISTINCT ath.Nom)      as "NbAthl"
    FROM ATHLETE as ath 
    LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
    LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
    LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
    LEFT JOIN 
    (SELECT
        cmp.SaisonAnnee             as "Saison",
        """ + txt_qry + """,
        CASE cat."CateAge" 
            WHEN 'U10' THEN 'U10/U13'
            WHEN 'U13' THEN 'U10/U13'
            WHEN 'U15' THEN 'U15/U17'
            WHEN 'U17' THEN 'U15/U17'
            WHEN 'U20' THEN 'U20'
            ELSE 'SEN'
        END                           as "CateAge",
        COUNT(1)     as "Nb_Part",
        COUNT(DISTINCT ath.Nom)      as "Nb_Athl",
        ROW_NUMBER() OVER (PARTITION BY cmp.SaisonAnnee,
            CASE cat."CateAge" 
                WHEN 'U10' THEN 'U10/U13'
                WHEN 'U13' THEN 'U10/U13'
                WHEN 'U15' THEN 'U15/U17'
                WHEN 'U17' THEN 'U15/U17'
                WHEN 'U20' THEN 'U20'
                ELSE 'SEN'
            END
            ORDER BY COUNT(1) DESC) as row_num_nb_part,
        ROW_NUMBER() OVER (PARTITION BY cmp.SaisonAnnee,
            CASE cat."CateAge" 
                WHEN 'U10' THEN 'U10/U13'
                WHEN 'U13' THEN 'U10/U13'
                WHEN 'U15' THEN 'U15/U17'
                WHEN 'U17' THEN 'U15/U17'
                WHEN 'U20' THEN 'U20'
                ELSE 'SEN'
            END
            ORDER BY COUNT(DISTINCT ath.Nom) DESC) as row_num_nb_athl
        FROM ATHLETE as ath 
        LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
        LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
        LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
        GROUP BY cmp.SaisonAnnee, """ + txt_qry + """, 
            CASE cat."CateAge" 
                WHEN 'U10' THEN 'U10/U13'
                WHEN 'U13' THEN 'U10/U13'
                WHEN 'U15' THEN 'U15/U17'
                WHEN 'U17' THEN 'U15/U17'
                WHEN 'U20' THEN 'U20'
                ELSE 'SEN'
            END) as rclb
    ON rclb.Saison = cmp.SaisonAnnee
    AND rclb.CateAge = CASE cat."CateAge" 
        WHEN 'U10' THEN 'U10/U13'
        WHEN 'U13' THEN 'U10/U13'
        WHEN 'U15' THEN 'U15/U17'
        WHEN 'U17' THEN 'U15/U17'
        WHEN 'U20' THEN 'U20'
        ELSE 'SEN'
    END
    AND r""" + txt_qry + """ = """ + txt_qry + """
    GROUP BY cmp.SaisonAnnee, """ + txt_qry + """, 
        CASE
            WHEN cat."CateAge" IN ('U10','U13') THEN 'U10/U13'
            WHEN cat."CateAge" IN ('U15','U17') THEN 'U15/U17'
            WHEN cat."CateAge" = 'U20' THEN 'U20'
            ELSE 'SEN'
        END
          """
    df_ac = pd.read_sql_query(qry_age, conn)
    df_ac.head()
    print(df_ac)
    print(txt_club)
    print(selected_year)

    list_cateage=['U10/U13', 'U15/U17', 'U20', 'SEN']

    updated_show = [{'display': 'none'}] * 4
    nb_part = ['0 Participations'] * 4
    rang_part = [''] * 4
    rang_athl = ['0 Athlètes'] * 4
    nb_athl = [''] * 4

    n = 0
    for i in list_cateage:
        if disp_cards:
            if mode_ligue == True:
                df_cate = df_ac[(df_ac['Ligue'].isin(txt_ligue)) & (df_ac['CateAge'] == i) & (df_ac['Saison'] == selected_year)]
            else:
                df_cate = df_ac[(df_ac['Club'].isin(txt_club)) & (df_ac['CateAge'] == i) & (df_ac['Saison'] == selected_year)]
            updated_show[n] = {'display': 'block'}
            if not df_cate.empty:

                nb_part[n] = str(df_cate['NbPart'].values[0]) + ' Participations'
                if df_cate['RangPartClubCateAge'].values[0] == 1:
                    end_txt = 'er)'
                else:
                    end_txt = 'ème)'
                rang_part[n] = ' (' + str(df_cate['RangPartClubCateAge'].values[0]) + end_txt

                nb_athl[n] = str(df_cate['NbAthl'].values[0]) + ' Athlètes'
                if df_cate['RangAthlClubCateAge'].values[0] == 1:
                    end_txt = 'er)'
                else:
                    end_txt = 'ème)'
                rang_athl[n] = ' (' + str(df_cate['RangAthlClubCateAge'].values[0]) + end_txt
            n = n+1

    return  updated_show[0], f"{nb_part[0]}" + f"{rang_part[0]}", f"{nb_athl[0]}" + f"{rang_athl[0]}", \
            updated_show[1], f"{nb_part[1]}" + f"{rang_part[1]}", f"{nb_athl[1]}" + f"{rang_athl[1]}", \
            updated_show[2], f"{nb_part[2]}" + f"{rang_part[2]}", f"{nb_athl[2]}" + f"{rang_athl[2]}",\
            updated_show[3], f"{nb_part[3]}" + f"{rang_part[3]}", f"{nb_athl[3]}" + f"{rang_athl[3]}"




# Partie + Info
def qry_box(txt_club_ligue, txt_ligue, selected_year):
    if not txt_ligue:
        txt_club = ''
    else:
        txt_club = ', clb.Club'
    qry = """SELECT cmp.SaisonAnnee as "Saison", """ + txt_club + """ ath.Nom, count(clb.club) as "Nb Compet" 
                     , max(cat.Arrache) as "Max Arr", max(cat.EpJete) as "Max EpJ", max(cat.PoidsTotal) as "Max Tot"
                     , max(round(cat.IWF_Calcul,3)) as "Max IWF"
                     , CASE 
                            WHEN cat."CateAge" = 'U10' THEN 'U10'
                            WHEN cat."CateAge" = 'U13' THEN 'U13'
                            WHEN cat."CateAge" = 'U15' THEN 'U15'
                            WHEN cat."CateAge" = 'U17' THEN 'U17'
                            WHEN cat."CateAge" = 'U20' THEN 'U20'
                            ELSE 'SEN'
                        END as "CateAge"
                    , atr.AthlRang as "Classement Fr"
                      FROM ATHLETE as ath
                      LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID
                      LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                      LEFT JOIN CLUB as clb on clb.Club = cat.CATClub

                      LEFT JOIN (
                        select
                            cmp.SaisonAnnee
                          , ath.Nom
                          , cat.Sexe
                          , CASE 
                                WHEN cat."CateAge" = 'U10' THEN 'U10'
                                WHEN cat."CateAge" = 'U13' THEN 'U13'
                                WHEN cat."CateAge" = 'U15' THEN 'U15'
                                WHEN cat."CateAge" = 'U17' THEN 'U17'
                                WHEN cat."CateAge" = 'U20' THEN 'U20'
                                ELSE 'SEN'
                            END as "CateAge"
                          , max(round(cat.IWF_Calcul,3)) as "IWF"
                          , row_number() over(partition by cmp."SaisonAnnee", cat.Sexe,
                          CASE WHEN cat."CateAge" = 'U10' THEN 'U10' WHEN cat."CateAge" = 'U13' THEN 'U13' WHEN cat."CateAge" = 'U15' THEN 'U15' WHEN cat."CateAge" = 'U17' THEN 'U17'
                          WHEN cat."CateAge" = 'U20' THEN 'U20' ELSE 'SEN' END
                          order by max(round(cat.IWF_Calcul,3)) desc) as "AthlRang"

                          FROM ATHLETE as ath
                          LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID
                          LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                          group by cmp.SaisonAnnee, ath.Nom) as atr
                                on atr.Nom = ath.Nom
                                and atr.SaisonAnnee = cmp.SaisonAnnee

                      where """ + txt_club_ligue + """
                          and cmp.SaisonAnnee = """ + str(selected_year) + """
                      group by cmp.SaisonAnnee, clb.club, ath.Nom, atr.AthlRang,
                        CASE WHEN cat."CateAge" = 'U10' THEN 'U10' WHEN cat."CateAge" = 'U13' THEN 'U13' WHEN cat."CateAge" = 'U15' THEN 'U15' WHEN cat."CateAge" = 'U17' THEN 'U17'
                            WHEN cat."CateAge" = 'U20' THEN 'U20' ELSE 'SEN' END
                      order by atr.AthlRang"""
    return qry


@callback(
    Output("u10_u13-modal", "is_open"),
    [Input("open_u10_u13", "n_clicks"),
     Input("close-u10_u13", "n_clicks")],
    State("u10_u13-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_athl(open_clicks, close_clicks, is_open_u10_u13):
    if open_clicks or close_clicks:
        return not is_open_u10_u13
    return is_open_u10_u13

# +Info Carte 1
@callback(
    [
    #Output("u10_u13-graph", "figure"),
    #Output("u10_u13-graph", "style"),
     Output("u10_u13-table", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value'),
     Input("u10_u13-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(selected_year, txt_ligue, txt_club, is_open_u10_u13):
    if not is_open_u10_u13 or (not txt_ligue and not txt_club):
        raise PreventUpdate
    if is_open_u10_u13:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        if txt_club:
            txt_club_ligue = "clb.club in ('" + txt_club[0] + "')"
        else:
            txt_club_ligue = "clb.ligue in ('" + txt_ligue[0] + "')"

        qry = qry_box(txt_club_ligue, txt_ligue, selected_year)

        df_u10_u13 = pd.read_sql_query(qry, conn)
        df_u10_u13 = df_u10_u13[df_u10_u13['CateAge'].isin(['U10','U13'])]
        print(df_u10_u13)
        df_u10_u13.head()

        return [dbc.Table.from_dataframe(df_u10_u13, responsive=True, striped=True, bordered=True, hover=True)]
        #fig_athl1, display_graph_athl1,

@callback(
    Output("u15_u17-modal", "is_open"),
    [Input("open_u15_u17", "n_clicks"),
     Input("close-u15_u17", "n_clicks")],
    State("u15_u17-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_athl(open_clicks, close_clicks, is_open_u15_u17):
    if open_clicks or close_clicks:
        return not is_open_u15_u17
    return is_open_u15_u17


# +Info Carte 2
@callback(
    [
    #Output("u15_u17-graph", "figure"),
    #Output("u15_u17-graph", "style"),
     Output("u15_u17-table", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value'),
     Input("u15_u17-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(selected_year, txt_ligue, txt_club, is_open_u15_u17):
    if not is_open_u15_u17 or (not txt_ligue and not txt_club):
        raise PreventUpdate
    if is_open_u15_u17:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        if txt_club:
            txt_club_ligue = "clb.club in ('" + txt_club[0] + "')"
        else:
            txt_club_ligue = "clb.ligue in ('" + txt_ligue[0] + "')"

        qry = qry_box(txt_club_ligue, txt_ligue, selected_year)

        df_u15_u17 = pd.read_sql_query(qry, conn)
        df_u15_u17 = df_u15_u17[df_u15_u17['CateAge'].isin(['U15', 'U17'])]
        print(df_u15_u17)
        df_u15_u17.head()

        return [dbc.Table.from_dataframe(df_u15_u17, responsive=True, striped=True, bordered=True, hover=True)]
        #fig_athl1, display_graph_athl1,
    
@callback(
    Output("u20-modal", "is_open"),
    [Input("open_u20", "n_clicks"),
     Input("close-u20", "n_clicks")],
    State("u20-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_athl(open_clicks, close_clicks, is_open_u20):
    if open_clicks or close_clicks:
        return not is_open_u20
    return is_open_u20
# +Info Carte 3
@callback(
    [
    #Output("u20-graph", "figure"),
    #Output("u20-graph", "style"),
     Output("u20-table", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value'),
     Input("u20-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(selected_year, txt_ligue, txt_club, is_open_u20):
    if not is_open_u20 or (not txt_ligue and not txt_club):
        raise PreventUpdate
    if is_open_u20:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        if txt_club:
            txt_club_ligue = "clb.club in ('" + txt_club[0] + "')"
        else:
            txt_club_ligue = "clb.ligue in ('" + txt_ligue[0] + "')"

        qry = qry_box(txt_club_ligue, txt_ligue, selected_year)

        df_u20 = pd.read_sql_query(qry, conn)
        df_u20 = df_u20[df_u20['CateAge'].isin(['U20'])]
        print(df_u20)
        df_u20.head()

        return [dbc.Table.from_dataframe(df_u20, responsive=True, striped=True, bordered=True, hover=True)]
        #fig_athl1, display_graph_athl1,


@callback(
    Output("sen-modal", "is_open"),
    [Input("open_sen", "n_clicks"),
     Input("close-sen", "n_clicks")],
    State("sen-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal_athl(open_clicks, close_clicks, is_open_sen):
    if open_clicks or close_clicks:
        return not is_open_sen
    return is_open_sen
# +Info Carte 4
@callback(
    [
    #Output("sen-graph", "figure"),
    #Output("sen-graph", "style"),
     Output("sen-table", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value'),
     Input("sen-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(selected_year, txt_ligue, txt_club, is_open_sen):
    if not is_open_sen or (not txt_ligue and not txt_club):
        raise PreventUpdate
    if is_open_sen:
        dirname = os.path.dirname(__file__)
        path_db = os.path.join(dirname, 'dataltero.db')
        conn = sql.connect(database=path_db)

        if txt_club:
            txt_club_ligue = "clb.club in ('" + txt_club[0] + "')"
        else:
            txt_club_ligue = "clb.ligue in ('" + txt_ligue[0] + "')"

        qry = qry_box(txt_club_ligue, txt_ligue, selected_year)

        df_sen = pd.read_sql_query(qry, conn)
        df_sen = df_sen[df_sen['CateAge'].isin(['SEN'])]
        print(df_sen)
        df_sen.head()

        return [dbc.Table.from_dataframe(df_sen, responsive=True, striped=True, bordered=True, hover=True)]
        #fig_athl1, display_graph_athl1,


if __name__ == '__main__':
    run_server(debug=True)
