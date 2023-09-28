import dash
from dash import html, dcc

app = dash.Dash(__name__, use_pages=True)
server = app.server

app.layout = html.Div(
    [
        # main app framework
        html.Div("Dashboard Data Haltero",
        style={'fontSize':40,
               'textAlign':'center',
               'color': 'White',
               'backgroundColor': 'rgb(0, 0, 131)',
               'font-family': 'Segoe UI'}),
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
        html.Div(className='hr4'),

        # content of each page
        dash.page_container
    ]
)


if __name__ == "__main__":
    app.run(debug=True)