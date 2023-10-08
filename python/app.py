import dash
from dash import html, dcc, Input, Output, State, html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}],
                use_pages=True)

server = app.server

app.layout = \
    html.Div([
        dbc.Row([
            dbc.Col(
                # main app framework
                html.Div([
                    html.Div("Dashboard Data Haltero",
                    style={'fontSize':40,
                           'textAlign':'center',
                           'color': 'White',
                           'backgroundColor': 'rgb(0, 0, 131)',
                           'font-family': 'Segoe UI'}),

                            html.Div([
                                dbc.Button("Info", id="open", color="info", outline=True, className="me-1"),
                                dbc.Modal([
                                        dbc.ModalHeader("Information"),
                                        dbc.ModalBody([
                                            html.P("Développé par Joris Dawid (CH Arbresle)"),
                                            html.P("📧 joris.dawid@gmail.com"),
                                        ]),
                                        dbc.ModalFooter(
                                            dbc.Button("Close", id="close-button", color="secondary", className="ml-auto")
                                        ),
                                    ], id="info-modal", size="lg", centered=True, is_open=False),
                            ], className='info_button'),
                            html.Div([
                                dcc.Link(page['name']+"  |  ",
                                         href=page['path'],
                                         style = {'fontSize': 20,
                                         'color': 'White',
                                         'backgroundColor': 'rgba(0,0,0,0.5)',
                                         'font-family': 'Segoe UI'}, className='links')
                                for page in dash.page_registry.values()
                                ],
                                className='link_zone'
                            ),
                    html.Div(className='hr1'),
                    html.Div(className='hr2'),
                    html.Div(className='hr3'),
                    html.Div(className='hr4')])
            , width=12)
        ]),

        # content of each page


        dash.page_container

    ]
)

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