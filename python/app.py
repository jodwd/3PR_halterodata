import dash
from dash import html, dcc, Input, Output, State, html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import sqlite3 as sql
import pandas as pd
import os
import dash_daq as daq
from datetime import datetime, timedelta
from dash_bootstrap_components._components.Container import Container



app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
                use_pages=True)
app.title = "3PR - Dashboard Haltero"
server = app.server

# Connection à la base SQLite
dirname = os.path.dirname(os.path.abspath(__file__))
path_db = os.path.join(dirname, 'pages/dataltero.db')
conn = sql.connect(database=path_db)

# Requête
qry = """SELECT max(cmp.DateCompet) as "Date"
      FROM COMPET as cmp """
df = pd.read_sql_query(qry, conn)
df.head()

nav_button = \
    dbc.Row([
        dbc.Col([
            dbc.Button(
                "Athletes", outline=True, color="danger", className="me-1", href="/", size="sm")
            ],  width="auto", align="center"),
        dbc.Col([
            dbc.Button(
                "Clubs", outline=True, color="primary", className="me-1", href="/club", size="sm")
            ],  width="auto", align="center"),
        dbc.Col([
            dbc.Button(
                "Listings", outline=True, color="warning", className="me-1", href="/listings", size="sm")
            ],  width="auto", align="center"),
            #], xs=2, sm=2, md=2, lg=2, xl=2, align="center")
        dbc.Col([
            dbc.Button("🤔 Aide", id="open", color="success", outline=True, className="me-1", size="sm"),
            dbc.Modal([
                dbc.ModalHeader("Informations & Aide"),
                dbc.ModalBody([
                    html.P("🐓 Basé sur les données FFHM Scoresheet"),
                    html.P("🏋️ Données à jour au " + df.iloc[0,0]),
                    html.P("👨‍💻 https://github.com/jodwd/3PR_halterodata"),
                    html.P("📧 trois3pr@gmail.com"),
                    html.Div([], id="help-txt"),
                ]),
                dbc.ModalFooter(
                    dbc.Button("Fermer", id="close-button", color="secondary", className="ml-auto", size="sm")
                ),
                ], id="info-modal", size="lg", centered=True, is_open=False),
            ],  width="auto"),
        dbc.Col([
            dbc.Button("🎂", id="anniv", color="light", outline=True, className="me-1", size="sm"),
            dbc.Modal([
                dbc.ModalHeader("🎂"),
                dbc.ModalBody([
                    html.Div([html.P("")], id="txt_anniv")
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-button-anniv", color="secondary", className="ml-auto")
                ),
                ], id="anniv-modal", size="lg", centered=True, is_open=False),
            ],  width="auto"),

     #   dbc.Col([
     #      html.Div([
     #          daq.BooleanSwitch(
     #              id='our-boolean-switch',
     #              label="Mode Nuit",
     #              on=False),
     #          html.Div(id='boolean-switch-result')
     #      ])
     #      ],  width="auto"),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.Div(dcc.Location(id="url")),
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=r'assets/3PR.png', height="52px")),
                        dbc.Col(dbc.NavbarBrand("Tableau de Bord Haltero", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                nav_button,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
)

app.layout = \
html.Div(children=
#dbc.Container(
    [navbar,
    html.Div(className='hr1'),
    html.Div(className='hr2'),
    html.Div(className='hr3'),
    html.Div(className='hr4'),
    dash.page_container],
    #fluid=True,
    id="page-content"
)

#Boutons de Navigation
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#Bouton Info
@app.callback(
    Output("info-modal", "is_open"),
    [Input("open", "n_clicks"),
    Input("close-button", "n_clicks")],
    State("info-modal", "is_open"),
)

def toggle_info_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    print(str(is_open))
    return is_open


@app.callback(
    [Output("help-txt", "children")],
    [Input("url", "pathname"),
    Input("info-modal", "is_open")],
    prevent_initial_call=True
)

def page_info(path_name, is_open):
    if not is_open:
        raise PreventUpdate
    else:
        print(path_name)
        help_div = []
        if str(path_name) == '/' or str(path_name) == '' or str(path_name) == '/athletes':
            help_div = [html.H3("Dashboard Athlètes"),
                        html.P("On peut suivre les performances détaillées d'un athlète et les comparer à d'autres athlètes"),
                        html.P("Quand on choisit un athlète une carte apparait en haut qui donne des informations clés sur l'athlète.",
                              "On peut également cliquer sur +Info pour afficher ses performances depuis le début de Scoresheet."),

                        html.Img(src=r'assets/01_aide_2.png', width="90%"),
                        html.P("Seules les cartes des 4 premiers athlètes seront affichées mais on peut en choisir plus et les résultats "
                               "apparaitront dans le graphique et le tableau. "
                               "En survolant un point du graphique le détail de la performance apparait."),
                        html.Img(src=r'assets/01_aide_1.png', width="90%")]
        if str(path_name) == '/club':
            help_div = [html.H3("Dashboard Clubs"),
                        html.P("Cette page permet de suivre les performances de son club ou de sa ligue"),
                        html.P("Une fois son club ou sa ligue choisi on voit apparaitre en haut le classement du club par catégorie d'âge"
                               "Par rapport à tous les clubs de France."),
                        html.Img(src=r'assets/02_aide_1.png', width="90%"),
                        html.P("Si on clique sur '+Info' on verra apparaitre la liste des athlètes du club et leur classement au niveau national."),
                        html.Img(src=r'assets/02_aide_2.png', width="90%"),
                        html.P("En bas on obtient le classement H et F des athlètes du club et les points en équipe avec les meilleurs athlètes réalisant"
                               "leurs meilleures performances"),
                        html.Img(src=r'assets/02_aide_3.png', width="90%")]
        if str(path_name) == '/listings':
            help_div = [html.H3("Listings"),
                        html.P("Cette page permet de suivre les classement des athlètes"),
                        html.P("Le classement se fait sur la meilleure performance au coefficient IWF/Sinclair sur l'année de chaque athlètes"
                               "sauf si on filtre par catégorie de poids et/ou série et dans ce cas on affichera le meilleur total de chaque athlète par catégorie"),
                        html.P("On peut sélectionner plusieurs critères pour chaque filtre."),
                        html.P("Si on filtre sur les catégories U10 ou U13 cela affiche le total et le coefficient IWF sur 2 essais réussis.")
                        ]

        return [help_div]

@app.callback(
    Output("anniv-modal", "is_open"),
    [Input("anniv", "n_clicks"),
    Input("close-button-anniv", "n_clicks")],
    State("anniv-modal", "is_open"),
)

def toggle_anniv_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open

@app.callback(
    [Output("txt_anniv", "children")],
    [Input("anniv-modal", "is_open")],
    prevent_initial_call=True
)

def anniv(is_open):
    if not is_open:
        raise PreventUpdate
    if is_open:
        dirname = os.path.dirname(os.path.abspath(__file__))
        path_db = os.path.join(dirname, 'pages/dataltero.db')
        conn = sql.connect(database=path_db)

        qry_anniv = """SELECT DISTINCT
                        ath.Nom || ' (' || Cast((JulianDay(DATETIME('now')) - JulianDay(DATETIME(substr(ath."DateNaissance",7,4)
                        || '-' || substr(ath."DateNaissance",4,2) || '-' || substr(ath."DateNaissance",1,2)))) / 365 AS Integer) || ' ans)' AS "AthlAnniv"
                    FROM
                        ATHLETE as ath
                        LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID = ath.AthleteID
                        LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition
                        LEFT JOIN ATHLETE_PR apr on apr."AthleteID" = (ath.Nom || ath."DateNaissance")
                                                  and apr.SaisonAnnee = cmp.SaisonAnnee
                    WHERE substr(DateNaissance, 1, 5) = substr(DATETIME('now'), 9,2) || '/' || substr(DATETIME('now'), 6 ,2)
                        AND (cmp.SaisonAnnee = cast(substr(DATE('now', '-8 months'),1,4) as Integer)
                        OR  cmp.SaisonAnnee = cast(substr(DATE('now', '+4 months'),1,4) as Integer))

                    ORDER BY
                        (case when cat.Sexe='F' then 1.5 else 1 end)* apr."MaxIWFSaison" DESC"""

        df_anniv = pd.read_sql_query(qry_anniv, conn)
        df_anniv.head()
        print(df_anniv)

        today = datetime.now()
        txt_anniv = today.strftime("%d/%m") + ' - Joyeux anniversaire à '
        for i in df_anniv['AthlAnniv'].tolist():
            txt_anniv = txt_anniv + i + ', '
        txt_anniv = txt_anniv[0:-2]

        return [txt_anniv]




if __name__ == "__main__":
    app.run(debug=True)