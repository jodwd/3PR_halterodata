import dash
from dash import  dcc, Input, Output, State, html, clientside_callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import sqlite3 as sql
import pandas as pd
import os
import dash_daq as daq
from datetime import datetime
import dash_breakpoints
import time

print("0 start : " + str(time.time()))
app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
                use_pages=True)
app.title = "3PR - Tableau de Bord de l'Haltérophilie en France"
server = app.server

# Connection à la base SQLite
dirname = os.path.dirname(os.path.abspath(__file__))
dirname = os.path.dirname(__file__)
file_path = os.path.join(
    dirname,
    "pages",
    "parquet_tables",
    "REPORT_ATHLETES.parquet"
)

# Requête TODO : associer les IWF Max à une compétition précise (lieu, date...) dans la BDD
df = pd.read_parquet(file_path, engine='fastparquet')
df = df["DateCompet"].max()

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
                    html.P("🐓 Basé sur les données de toutes les compétitions closes de Scoresheet FFHM"),
                    html.P("🔄 Mise à Jour tous les week-ends"),
                    html.P("🏋️ Données à jour au " + df.iloc[0,0]),
                    html.P("👨‍💻 Repo : https://github.com/jodwd/3PR_halterodata"),
                    html.P("📷 Insta : @3pr.fr"),
                    html.P("📧 Mail : trois3pr@gmail.com"),
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
                    dbc.Button("Fermer", id="close-button-anniv", color="secondary", className="ml-auto")
                ),
                ], id="anniv-modal", size="lg", centered=True, is_open=False),
            ],  width="auto"),

        dbc.Col([
           html.Div([
                html.P("     ")
           ])
        ],  width="auto"),

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
                        dbc.Col(html.Img(src=r'assets/3PR.png', height="68px")),
                        dbc.Col(dbc.NavbarBrand("Perfs Haltero  ", className="ms-2", style={"color": "white", 'font-size': "20px"}, id="nav_brand")),

                    ],
                    align="center",
                    className="g-0",
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
           # dbc.Col([
           #     html.P("Nouveau : Testez vos connaissances avec la fonctionnalité 'Quizz' sur la page Listing !", style = {"color": "white", 'font-size': "12px"})
           # ], xs=8, sm=6, md=3, lg=2, xl=2, align="center"),
            dbc.Col([
                daq.BooleanSwitch(
                    id='bool_light',
                    label={"label": "🌙/🌞", 'style': {"color": "white"}},
                    labelPosition="bottom",
                    on=False),
            ], width="auto"),


            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                nav_button,
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    id="navbar_cont",
    color="dark",
    fixed="top",
    sticky="top",
    dark=True,
)

app.layout = \
html.Div(children=[
    html.Div(id="display", className="display_screen_width", hidden=False),
    dash_breakpoints.WindowBreakpoints(
        id="breakpoints",
        widthBreakpointThresholdsPx=[576, 768, 992, 1200, 1400],
        widthBreakpointNames=["xs", "sm", "md", "lg", "xl", "xxl"]
    ),
    navbar,
    html.Div(className='hr1'),
    html.Div(className='hr2'),
    html.Div(className='hr3'),
    html.Div(className='hr4'),
    dash.page_container],
    #fluid=True,
    id="page-content"
)


# On change le titre en fonction de la taille de l'écran
clientside_callback(
    """(wBreakpoint, w) => {
        console.log("Only updating when crossing the threshold")
        return wBreakpoint
    }""",
    Output("display", "children"),
    Input("breakpoints", "widthBreakpoint"),
    State("breakpoints", "width"),
)
@app.callback(
    Output("nav_brand", "children"),
    Input("display", "children"),
    prevent_initial_call=True
)

def change_title_screensize(breakpoint_str):
    breakpoint_name = breakpoint_str
    if breakpoint_name=="xs" or breakpoint_name=="sm":
        nav_txt = "Perfs Haltero  "
    elif breakpoint_name=="md":
        nav_txt = "Tableau de bord Haltero"
    elif breakpoint_name=="lg" or breakpoint_name=="xl":
        nav_txt = "Tableau de bord des Performances en Haltérophilie  "
    else:
        nav_txt = "Tableau de bord des Performances en Haltérophilie en France  "
    print(breakpoint_name)
    return nav_txt



#Boutons de Navigation
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
    prevent_initial_call=True
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
    prevent_initial_call=True
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
            help_div = [html.H3("Perfs Athlètes"),
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
                        html.P("Si on filtre par catagorie d'âge, le classement par âge et au pour tous les âges s'affichera dans cet ordre à gauche du nom de l'athlète."),
                        html.P("Si on filtre sur les catégories U10 ou U13 cela affiche le total et le coefficient IWF sur 2 essais réussis.")
                        ]

        return [help_div]

@app.callback(
    Output("anniv-modal", "is_open"),
    [Input("anniv", "n_clicks"),
    Input("close-button-anniv", "n_clicks")],
    State("anniv-modal", "is_open"),
    prevent_initial_call=True
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
        file_path = os.path.join(
            dirname,
            "parquet_tables",
            "REPORT_ANNIV.parquet"
        )
        df_anniv = pd.read_parquet(file_path, engine='fastparquet')
        print(df_anniv)

        today = datetime.now()
        txt_anniv = today.strftime("%d/%m") + ' - Joyeux anniversaire à '
        for i in df_anniv['AthlAnniv'].tolist():
            txt_anniv = txt_anniv + i + ', '
        txt_anniv = txt_anniv[0:-2]

        return [txt_anniv]


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3500))
    app.run(host="0.0.0.0", port=port, debug=False)