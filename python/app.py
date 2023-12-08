import dash
from dash import html, dcc, Input, Output, State, html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import sqlite3 as sql
import pandas as pd
import os
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

nav_button = dbc.Row(
    [
        dbc.Col([
            dbc.Button(
                "Athletes", outline=True, color="danger", className="me-1", href="/")
            ], width="auto", align="center"),
        dbc.Col([
            dbc.Button(
                "  Club  ", outline=True, color="primary", className="me-1", href="/club")
            ], width="auto", align="center"),
        dbc.Col([
            dbc.Button(
                "Listings", outline=True, color="warning", className="me-1", href="/listings")
            ], width="auto", align="center"),
            #], xs=2, sm=2, md=2, lg=2, xl=2, align="center")
        dbc.Col([
            dbc.Button("Info", id="open", color="success", outline=True, className="me-1"),
            dbc.Modal([
                dbc.ModalHeader("Information"),
                dbc.ModalBody([
                    html.P("🐓 Basé sur les données FFHM Scoresheet"),
                    html.P("🏋️ Données à jour au " + df.iloc[0,0]),
                    html.P("👨‍💻 https://github.com/jodwd/3PR_halterodata"),
                    html.P("📧 trois3pr@gmail.com"),
                    html.Div([html.P("")], id="txt_anniv")
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-button", color="secondary", className="ml-auto")
                ),
                ], id="info-modal", size="lg", centered=True, is_open=False),
            ],  width="auto"),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
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
dbc.Container(
    [navbar,
    html.Div(className='hr1'),
    html.Div(className='hr2'),
    html.Div(className='hr3'),
    html.Div(className='hr4'),
    dash.page_container],
    fluid=True,
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

def toggle_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open

@app.callback(
    [Output("txt_anniv", "children")],
    [Input("info-modal", "is_open")],
    prevent_initial_call=True
)

def update_table_athl2(is_open):
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
        print(today)
        txt_anniv = '🎂 ' + today.strftime("%d/%m") + ' - Joyeux anniversaire à '
        for i in df_anniv['AthlAnniv'].tolist():
            txt_anniv = txt_anniv + i + ', '
        txt_anniv = txt_anniv[0:-2]

        return [txt_anniv]




if __name__ == "__main__":
    app.run(debug=True)