import dash
import plotly.express as px
from dash import dash_table, dcc, html, callback
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
#import numpy as np
import os
from dash.dependencies import Input, Output
#from flask import Flask, render_template
import dash_bootstrap_components as dbc




def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


# Connection à la base SQLite
dirname = os.path.dirname(__file__)
path_db = os.path.join(dirname, 'dataltero.db')
conn = sql.connect(database=path_db)

# Requête
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
df = df

df['IWF'] = round(df['IWF'], 3)
df['MoisCompet'] = pd.Categorical(df['MoisCompet'],
                                  ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05", "06", "07"])

updated_title = 'Haltero Data'

# app = dash.Dash(__name__)
dash.register_page(__name__, path='/')
# server = server


# df_unique_names = df['Nom'].unique  # Fetch or generate data from Python
list_names = list(set(df['Nom'].tolist()))

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
                                placeholder="Choisir des athlètes...",
                                )
                            ],
                            className="input_box1",),
                        html.Datalist(id='Nom_athl')])
                ), xs=6, sm=6, md=6, lg=2, xl=2),

            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Div([html.P("Card 1")], id="athlete1_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete1_club"),
                                    html.Div([html.P("Naissance")], id="athlete1_anniv"),
                                    html.Div([html.P("Max")], id="athlete1_max")
                                  ],   className="card-text",
                                ),
                                dbc.Button(
                                    "+ Info", color="danger", className="mt-auto", size="sm"
                                ),
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
                                    html.Div([html.P("Naissance")], id="athlete2_anniv"),
                                    html.Div([html.P("Max")], id="athlete2_max")],   className="card-text",
                                ),
                                dbc.Button(
                                    "+ Info", color="primary", className="mt-auto", size="sm"
                                ),
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
                                    html.Div([html.P("Naissance")], id="athlete3_anniv"),
                                    html.Div([html.P("Max")], id="athlete3_max")],   className="card-text",
                                ),
                                dbc.Button(
                                    "+ Info", color="warning", className="mt-auto", size="sm"
                                ),
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
                                    html.Div([html.P("Naissance")], id="athlete4_anniv"),
                                    html.Div([html.P("Max")], id="athlete4_max")],   className="card-text",
                                ),
                                dbc.Button(
                                    "+ Info", color="success", className="mt-auto", size="sm"
                                ),
                            ]
                        ),
                    )
                ], id="athl_card4",  style= {'display': 'none'}),
            ], xs=6, sm=3, md=3, lg=2, xl=2),
        ],  className="top_zone",),

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
                    value=[df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()],
                    marks={str(year): str(year) for year in df['SaisonAnnee'].unique()},
                    id='year-slider',
                    className='slider_zone')],
                id='div_output',
                className='graph_box'
            ),
        ], width=12),
    ]),

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
                    filter_action="native",
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
                    row_selectable="multi",
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


# @callback(
#    Output('Nom_athl', 'children'),
#    [Input('my_txt_input', 'value')]
# )
# def update_datalist(input_value):
#    children = []  # List to store dynamic options
#
#    # Generate options based on input value
#    if input_value:
#        # Fetch or generate data based on input value
#        # For example, you can query a database or an API
#        # and append the options to the children list
#        children = [html.Option(value=val, children=val) for val in list_names]
#
#    return children\


@callback(
    Output('Nom_athl', 'children'),
    [Input('none', 'children')]
)
def update_datalist(none):
    children = []  # List to store dynamic options

    children = [html.Option(value=val, children=val) for val in list_names]

    return children


@callback(
    Output('my_txt_input', 'options'),
    Input('year-slider', 'value'),
    prevent_initial_call=True
)
def update_athletes_list(selected_year):
    filtered_df = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    options = [x for x in sorted(list_names)]
    return options


# @callback(
#    Output('datatable-interactivity-container', "children"),
#    Input('datatable-interactivity', "derived_virtual_data"),
#    Input('datatable-interactivity', "derived_virtual_selected_rows"))


@callback(
    [Output('graph-with-slider', 'figure'),
     Output('graph-with-slider', 'style')],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])
def update_figure(selected_year, txt_inserted):
    if selected_year == '':
        selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
    filtered_df = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if txt_inserted:
        filtered_df = filtered_df[(filtered_df['Nom'].isin(txt_inserted))]
        display_graph = {'display': 'block'}

        fig = px.scatter(filtered_df, x="Mois", y="IWF", hover_name="Competition", hover_data=["Arr", "EpJ", "PdC", "Série"],
                                      color="Nom", log_x=False, size_max=55,color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"], )
        fig.update_traces(marker=dict(size=10, symbol='circle') )
        fig.update_xaxes(categoryorder="category ascending")
        fig.update_yaxes(categoryorder="category ascending")
        fig.update_layout(transition_duration=5, plot_bgcolor='rgb(40,40,45)', paper_bgcolor='rgb(40,40,45)',
                          font_color="white", font_size=10,
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
        #filtered_df = filtered_df[(filtered_df['Nom'] == 'NoData')]
        fig = px.scatter()
        display_graph = {'display': 'none'}

    return fig, display_graph


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
        filtered_df = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    else:
        filtered_df = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

    columns = [
             {"name": i, "id": i, "selectable": True} for i in
             ['Nom',  'Date', 'PdC', 'Arr1', 'Arr2', 'Arr3', 'Arr', 'EpJ1', 'EpJ2', 'EpJ3', 'EpJ', 'Total', 'IWF', 'Série', 'Catégorie', 'Competition']
     ]

    filtered_df = filtered_df.sort_values(by=['IWF'], ascending=False)
    dat = filtered_df.to_dict('records')
    print(len(dat))

    return dat, columns


@callback(
    [Output('athl_card1', 'style'),
     Output("athlete1_nom", "children"),
     Output("athlete1_club", "children"),
     Output("athlete1_anniv", "children"),
     Output("athlete1_max", "children"),
     #Output("athlete1_total", "children"),
     #Output("athlete1_pdc", "children"),
     Output('athl_card2', 'style'),
     Output("athlete2_nom", "children"),
     Output("athlete2_club", "children"),
     Output("athlete2_anniv", "children"),
     Output("athlete2_max", "children"),
     #Output("athlete2_total", "children"),
     #Output("athlete2_pdc", "children"),
     Output('athl_card3', 'style'),
     Output("athlete3_nom", "children"),
     Output("athlete3_club", "children"),
     Output("athlete3_anniv", "children"),
     Output("athlete3_max", "children"),
     #Output("athlete3_total", "children"),
     #Output("athlete3_pdc", "children"),
     Output('athl_card4', 'style'),
     Output("athlete4_nom", "children"),
     Output("athlete4_club", "children"),
     Output("athlete4_anniv", "children"),
     Output("athlete4_max", "children")],
     #Output("athlete4_total", "children"),
     #Output("athlete4_pdc", "children")],

    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])

def updated_athletes(selected_year, txt_inserted):
    # Perform any manipulation on input_value and return the updated title
    updated_show = [{'display': 'none'}] * 4
    updated_name = [''] * 4
    updated_club = [''] * 4
    updated_anniv = [''] * 4
    updated_max = [''] * 4
    updated_arr = [''] * 4
    updated_epj = [''] * 4
    updated_total = [''] * 4
    updated_pdc = [''] * 4

    n = 0
    if txt_inserted is None:
        raise PreventUpdate
    txt_inserted=sorted(txt_inserted)
    for i in txt_inserted:
        print(str(min(selected_year)) + ' ' + i)
        updated_name[n] = i
        df1 = df[
            (df['Nom'] == i) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

        if len(df1['Club'].values[0]) > 21:
            updated_club[n] = df1['Club'].values[0][0:20] + '.'
        else:
            updated_club[n] = df1['Club'].values[0]
        updated_show[n] = {'display': 'block'}
        updated_anniv[n] = (df1['Né le'].values[0])[-4:]
        updated_max[n] = str(df1['IWF'].max()) + ' IWF'
        updated_arr[n] = str(df1['Arr'].max()) + '/'
        updated_epj[n] = str(df1['EpJ'].max()) + '/'
        updated_total[n] = df1['Total'].max()
        pdc_df = df1['Total'].idxmax()
        updated_pdc[n] = str(df.loc[pdc_df, 'PdC']) + 'kg'
        n = n + 1

    return updated_show[0], f"{updated_name[0]}", f"{updated_club[0]}", f"{updated_anniv[0]}", f"{updated_max[0]}",\
        updated_show[1], f"{updated_name[1]}", f"{updated_club[1]}", f"{updated_anniv[1]}", f"{updated_max[1]}",  \
        updated_show[2], f"{updated_name[2]}", f"{updated_club[2]}", f"{updated_anniv[2]}", f"{updated_max[2]}", \
        updated_show[3], f"{updated_name[3]}", f"{updated_club[3]}", f"{updated_anniv[3]}", f"{updated_max[3]}" #f"{updated_arr[3]}{updated_epj[3]}{updated_total[3]}", f"{updated_pdc[3]}",


@app.callback(
    Output("athl1-modal", "is_open"),
    [Input("open", "n_clicks"),
    Input("close-button", "n_clicks")],
    State("athl1-modal", "is_open"),
)

def toggle_modal(open_clicks, close_clicks, is_open):
    if open_clicks or close_clicks:
        return not is_open
    return is_open

if __name__ == '__main__':
    run_server(debug=True)

