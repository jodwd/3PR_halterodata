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
            ,   cat.EpJete          as "EpJ"
            ,   cat.PoidsTotal      as "Tot"
            ,   cat.PoidsDeCorps    as "PdC"
            ,   cat.IWF_Calcul      as "IWF"   
            ,   apr.SaisonAnnee     as "SaisonAnnee"
            ,   apr.MaxIWFSaison    as "Max IWF"
            ,   row_number() over(partition by ath.Nom, apr."SaisonAnnee" order by cat.IWF_Calcul desc) as "RowNum"
          FROM ATHLETE as ath 
          LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
          LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
          LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
          LEFT JOIN ATHLETE_PR as apr on apr.AthleteID = ath.AthleteID and apr.SaisonAnnee = cmp.SaisonAnnee)
      WHERE RowNum=1"""

df = pd.read_sql_query(qry, conn)
df.head()

df['Max IWF']=round(df['Max IWF'], 3)
df['Max IWF']=round(df['Max IWF'], 3)

dfh = df
dff = df
dfh['Rang'] = df[(df['Sexe'] == 'M') & df['SaisonAnnee'] == max(df['SaisonAnnee'])].groupby(['SaisonAnnee']).cumcount() + 1
dff['Rang'] = df[(df['Sexe'] == 'F') & df['SaisonAnnee'] == max(df['SaisonAnnee'])].groupby(['SaisonAnnee']).cumcount() + 1

updated_title='Dashboard Club'

#app = dash.Dash(__name__)
dash.register_page(__name__, name='Clubs', title='Dashboard Clubs', image='/assets/3PR.png', description='Tableau de bord des performances des clubs d''haltérophilie français')
#server = server


#df_unique_names = df['Nom'].unique  # Fetch or generate data from Python
nom_ligue = list(set(df['Ligue'].tolist()))
nom_club = list(set(df['Club'].tolist()))

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
            ],  xs=6, sm=6, md=6, lg=5, xl=5),
            dbc.Col([
                dcc.Dropdown(
                    options=[x for x in sorted(nom_club)],
                    multi=True,
                    id='txt-club',
                    placeholder="Club",
                    className="input-box",
                )
            ], xs=12, sm=12, md=12, lg=5, xl=5),
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

    # Nombre athlètes par catégorie
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
                            dbc.ModalHeader("Information", id="u10_u13_info"),
                            dbc.ModalBody([
                                dcc.Graph(id='u10_u13-graph', style={'display': 'none'}),
                                html.Div(id="u10_u13-table", className="athl_data_tab"),
                            ]),
                            dbc.ModalFooter(
                                dbc.Button("Close", id="close-u10_u13", color="secondary", className="ml-auto")
                            ),
                        ], id="u10_u13-modal", size="lg", centered=True, is_open=False),
                    ]
                ),
            ),
        ], id="cateage_card1", style={'display': 'none'}),
    ], xs=6, sm=3, md=3, lg=2, xl=2),
    
    
#     dbc.Col([
#         html.Div([
#             dbc.Card(
#                 dbc.CardBody(
#                     [
#                         html.Div([html.P("Card 2")], id="athlete2_nom", className="card-title"),
#                         html.Div([
#                             html.Div([html.P("Club")], id="athlete2_club"),
#                             html.Div([html.P("NaissanceMax")], id="athlete2_annivmax")], className="card-text",
#                         ),
#                         dbc.Button("+ Info", id="open_athl2", color="primary", className="mt-auto", size="sm"),
#                         dbc.Modal([
#                             dbc.ModalHeader("Information", id="athlete2_nom_info"),
#                             dbc.ModalBody([
#                                 dcc.Graph(id='athl2-graph', style={'display': 'none'}),
#                                 html.Div(id="athl2-table", className="athl_data_tab"),
#                             ]),
#                             dbc.ModalFooter(
#                                 dbc.Button("Close", id="close-athl2", color="secondary", className="ml-auto")
#                             ),
#                         ], id="athl2-modal", size="lg", centered=True, is_open=False),
#                     ]
#                 ),
#             )
#         ], id="athl_card2", style={'display': 'none'}),
#     ], xs=6, sm=3, md=3, lg=2, xl=2),
#     dbc.Col([
#         html.Div([
#             dbc.Card(
#                 dbc.CardBody(
#                     [
#                         html.Div([html.P("Card 3")], id="athlete3_nom", className="card-title"),
#                         html.Div([
#                             html.Div([html.P("Club")], id="athlete3_club"),
#                             html.Div([html.P("NaissanceMax")], id="athlete3_annivmax")], className="card-text",
#                         ),
#                         dbc.Button("+ Info", id="open_athl3", color="warning", className="mt-auto", size="sm"),
#                         dbc.Modal([
#                             dbc.ModalHeader("Information", id="athlete3_nom_info"),
#                             dbc.ModalBody([
#                                 dcc.Graph(id='athl3-graph', style={'display': 'none'}),
#                                 html.Div(id="athl3-table", className="athl_data_tab"),
#                             ]),
#                             dbc.ModalFooter(
#                                 dbc.Button("Close", id="close-athl3", color="secondary", className="ml-auto")
#                             ),
#                         ], id="athl3-modal", size="lg", centered=True, is_open=False),
#                     ]
#                 ),
#             )
#         ], id="athl_card3", style={'display': 'none'}),
#     ], xs=6, sm=3, md=3, lg=2, xl=2),
#     dbc.Col([
#         html.Div([
#             dbc.Card(
#                 dbc.CardBody(
#                     [
#                         html.Div([html.P("Card 4")], id="athlete4_nom", className="card-title"),
#                         html.Div([
#                             html.Div([html.P("Club")], id="athlete4_club"),
#                             html.Div([html.P("NaissanceMax")], id="athlete4_annivmax")], className="card-text",
#                         ),
#                         dbc.Button("+ Info", id="open_athl4", color="success", className="mt-auto", size="sm"),
#                         dbc.Modal([
#                             dbc.ModalHeader("Information", id="athlete4_nom_info"),
#                             dbc.ModalBody([
#                                 dcc.Graph(id='athl4-graph', style={'display': 'none'}),
#                                 html.Div(id="athl4-table", className="athl_data_tab"),
#                             ]),
#                             dbc.ModalFooter(
#                                 dbc.Button("Close", id="close-athl4", color="secondary", className="ml-auto")
#                             ),
#                         ], id="athl4-modal", size="lg", centered=True, is_open=False),
#                     ]
#                 ),
#             )
#         ], id="athl_card4", style={'display': 'none'}),
#     ], xs=6, sm=3, md=3, lg=2, xl=2),
# ], className="top_zone", ),

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
                    ['Rang', 'Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'Max IWF']
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
    [Output('datatable-h', "data"),
     Output('datatable-h', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value')
     ])

def update_data(selected_year=None, txt_ligue=None, txt_club=None):
    fdfh = df[(df['Sexe'] == 'M')]
    if selected_year == '':
        selected_year = fdfh['SaisonAnnee'].max()
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
            ['Rang', 'Nom', 'Arr', 'EpJ', 'Tot', 'PdC', 'Max IWF']
    ]

    dat = fdfh.to_dict('records')

    return dat, columns

@callback(
    [Output('datatable-f', "data"),
     Output('datatable-f', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value')
     ])

def update_data(selected_year, txt_ligue, txt_club):
    fdff = df[(df['Sexe'] == 'F')]
    if selected_year == '':
        selected_year = fdff['SaisonAnnee'].max()
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
            ['Rang', 'Nom', 'Arr', 'EpJ', 'Tot', 'PdC', 'Max IWF']
    ]

    dat = fdff.to_dict('records')

    return dat, columns

@callback(
    Output("top_5_h", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value')
     ])

def update_title(selected_year, txt_ligue, txt_club):
    # Perform any manipulation on input_value and return the updated title
    global updated_title_h
    fdfh = df[(df['Sexe'] == 'M')]
    if selected_year=='':
        selected_year=fdfh['SaisonAnnee'].max()
    if txt_ligue or txt_club:
        if txt_ligue:
            fdfh = fdfh[(fdfh['Ligue'].isin(txt_ligue)) & (fdfh['SaisonAnnee'] == selected_year)]
        if txt_club:
            fdfh = fdfh[(fdfh['Club'].isin(txt_club)) & (fdfh['SaisonAnnee'] == selected_year)]
    else:
        fdfh = fdfh[(fdfh['SaisonAnnee'] == selected_year)]

    fdfh=fdfh.sort_values(by=['Max IWF'], ascending=False)
    filtered_df=round(fdfh.head(5),0)
    res = filtered_df['Max IWF'].sum()
    updated_title_h = "Top 5 Hommes : " + str(int(res))

    return updated_title_h

@callback(
    Output("top_5_f", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value')
     ])

def update_title(selected_year, txt_ligue, txt_club):
    # Perform any manipulation on input_value and return the updated title
    global updated_title_f
    fdff = df[(df['Sexe'] == 'F')]
    if selected_year == '':
        selected_year = fdff['SaisonAnnee'].max()
    if txt_ligue or txt_club:
        if txt_ligue:
            fdff = fdff[
                (fdff['Ligue'].isin(txt_ligue)) & (fdff['SaisonAnnee'] == selected_year)]
        if txt_club:
            fdff = fdff[
                (fdff['Club'].isin(txt_club)) & (fdff['SaisonAnnee'] == selected_year)]
    else:
        fdff = fdff[(fdff['SaisonAnnee'] == selected_year)]

    fdff = fdff.sort_values(by=['Max IWF'], ascending=False)
    filtered_df=round(fdff.head(4),0)
    res = filtered_df['Max IWF'].sum()
    updated_title_f = "Top 4 Femmes : " + str(int(res))

    return updated_title_f

# Mise à jour des cartes par catégorie d'age
# Nb athletes (classement) / nb participations (Classement part)

@callback(
    [Output('cateage_card1', 'style'),
     Output("u10_u13_nb_athl", "children"),
     Output("u10_u13_nb_comp", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='txt-ligue', component_property='value'),
     Input(component_id='txt-club', component_property='value')
     ])

def updated_athletes(selected_year, txt_ligue, txt_club):
    # Perform any manipulation on input_value and return the updated title
    if txt_ligue is None and txt_club is None or len(txt_club) > 1:
        raise PreventUpdate


    print(txt_club)

    conn = sql.connect(database=path_db)
    qry_age = """SELECT
    cmp.SaisonAnnee             as "Saison",
    clb.club                    as "Club",
    CASE
        WHEN cat."CateAge" IN ('U10','U13') THEN 'U10/U13'
        WHEN cat."CateAge" IN ('U15','U17') THEN 'U15/U17'
        WHEN cat."CateAge" = 'U20' THEN 'U20'
        ELSE 'SE'
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
        clb.club,
        CASE cat."CateAge" 
            WHEN 'U10' THEN 'U10/U13'
            WHEN 'U13' THEN 'U10/U13'
            WHEN 'U15' THEN 'U15/U17'
            WHEN 'U17' THEN 'U15/U17'
            WHEN 'U20' THEN 'U20'
            ELSE 'SE'
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
                ELSE 'SE'
            END
            ORDER BY COUNT(1) DESC) as row_num_nb_part,
        ROW_NUMBER() OVER (PARTITION BY cmp.SaisonAnnee,
            CASE cat."CateAge" 
                WHEN 'U10' THEN 'U10/U13'
                WHEN 'U13' THEN 'U10/U13'
                WHEN 'U15' THEN 'U15/U17'
                WHEN 'U17' THEN 'U15/U17'
                WHEN 'U20' THEN 'U20'
                ELSE 'SE'
            END
            ORDER BY COUNT(DISTINCT ath.Nom) DESC) as row_num_nb_athl
    FROM ATHLETE as ath 
    LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
    LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
    LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
    GROUP BY cmp.SaisonAnnee, clb.club, 
        CASE cat."CateAge" 
            WHEN 'U10' THEN 'U10/U13'
            WHEN 'U13' THEN 'U10/U13'
            WHEN 'U15' THEN 'U15/U17'
            WHEN 'U17' THEN 'U15/U17'
            WHEN 'U20' THEN 'U20'
            ELSE 'SE'
        END) as rclb
ON rclb.Saison = cmp.SaisonAnnee
AND rclb.CateAge = CASE cat."CateAge" 
    WHEN 'U10' THEN 'U10/U13'
    WHEN 'U13' THEN 'U10/U13'
    WHEN 'U15' THEN 'U15/U17'
    WHEN 'U17' THEN 'U15/U17'
    WHEN 'U20' THEN 'U20'
    ELSE 'SE'
END
AND rclb.Club = clb.Club
GROUP BY cmp.SaisonAnnee, clb.club, 
    CASE
        WHEN cat."CateAge" IN ('U10','U13') THEN 'U10/U13'
        WHEN cat."CateAge" IN ('U15','U17') THEN 'U15/U17'
        WHEN cat."CateAge" = 'U20' THEN 'U20'
        ELSE 'SE'
    END
          """
    df_ac = pd.read_sql_query(qry_age, conn)
    df_ac.head()
    print(df_ac)
    print(txt_club)
    print(selected_year)
    df_f = df_ac[(df_ac['Club'].isin(txt_club)) & (df_ac['CateAge'] == "U10/U13") & (df_ac['Saison'] == selected_year)]
    updated_show = {'display': 'block'}
    nb_part_u10_u13 = df_f['NbPart'].values[0]
    rang_part_u10_u13 = df_f['RangPartClubCateAge'].values[0]
    rang_athl_u10_u13 = df_f['RangAthlClubCateAge'].values[0]
    nb_athl_u10_u13 = df_f['NbAthl'].values[0]


    return updated_show, f"{nb_part_u10_u13} Participations" + f" ({rang_part_u10_u13}ème)", f"{nb_athl_u10_u13} athlètes" + f" ({rang_athl_u10_u13}ème)"




# Partie + Info
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
# @callback(
#     [Output("u10_u13-graph", "figure"),
#      Output("u10_u13-graph", "style"),
#      Output("u10_u13-table", "children")],
#     [Input(component_id='txt-ligue', component_property='value'),
#      Input(component_id='txt-club', component_property='value'),
#      Input("u10_u13-modal", "is_open")],
#     prevent_initial_call=True
# )
# def update_table_athl1(txt_ligue, txt_club, is_open_u10_u13):
#     if not is_open_u10_u13 or (not txt_ligue and not txt_club):
#         raise PreventUpdate
#     if is_open_u10_u13:
#         dirname = os.path.dirname(__file__)
#         path_db = os.path.join(dirname, 'dataltero.db')
#         conn = sql.connect(database=path_db)
#
#         athl1 = txt_ligue[0]
#         qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
#                  max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
#                 , max(round(cat.IWF_Calcul,3)) as "IWF"
#               FROM ATHLETE as ath
#               LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID
#               LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition
#               LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
#
#               where ath.Nom='""" + athl1 + """'
#               group by cmp.SaisonAnnee, clb.club
#               order by cmp.SaisonAnnee asc"""
#         df_athl1 = pd.read_sql_query(qry, conn)
#         df_athl1.head()
#
#         df2_athl1 = df2[(df2['Nom'] == txt_ligue[0])]
#         df2_athl1['Série'] = pd.Categorical(df2_athl1['Série'],
#                                             ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A", "OLY"],
#                                             ordered=True)
#         df2_athl1 = df2_athl1.sort_values(by=['Série'])
#         print(df2_athl1)
#
#         fig_athl1 = px.histogram(df2_athl1, x="Série", color="Catégorie",
#                                  color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB",
#                                                           "purple", "#54B4D3", "#9FA6B2"],
#                                  category_orders={
#                                      "Série": ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "NAT", "INT B", "INT A",
#                                                "OLY"]})
#
#         fig_athl1.update_layout(font_size=12,
#                                 legend=dict(
#                                     orientation="h",
#                                     yanchor="bottom",
#                                     y=1.05,
#                                     xanchor="left",
#                                     x=-0.05
#                                 ))
#         display_graph_athl1 = {'display': 'block'}
#
#         return fig_athl1, display_graph_athl1, [
#             dbc.Table.from_dataframe(df_athl1, responsive=True, striped=True, bordered=True, hover=True)]



if __name__ == '__main__':
    run_server(debug=True)
