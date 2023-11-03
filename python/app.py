import dash
from dash import html, dcc, Input, Output, State, html
import dash_bootstrap_components as dbc
import os
from dash_bootstrap_components._components.Container import Container

app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
                use_pages=True)

server = app.server

HalDat_LOGO = os.path.join(dirname, 'assets/3PR.png')



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
                    html.P("Développé à partir des données FFHM Scoresheet"),
                    html.P("👨‍💻 https://github.com/jodwd/3PR_halterodata"),
                    html.P("📧 joris.dawid@gmail.com"),
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
                        dbc.Col(html.Img(src=HalDat_LOGO, height="52px")),
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
    fluid=True
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

if __name__ == "__main__":
    app.run(debug=True)