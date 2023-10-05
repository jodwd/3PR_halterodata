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
      , cat.Arr1, cat.Arr2, cat.Arr3, cat.Arrache as "Arraché", cat.Epj1, cat.Epj2, cat.Epj3, cat.EpJete as "EpJeté"
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
    html.Div([
        # Titre
        html.Div(
            children=[
                html.P("Dashboard Athlètes")
            ],
            id='filter_info',
            className="text-box",
        ),
        # Zone filtres athlètes
        html.Div([
            html.Div([
                # Selection Athlète #1
                # html.Div(
                #    children=[
                #        html.P("Athlète #1")
                #    ],
                #    id='athl1_info',
                #    className="athl1_box",
                # ),
                html.Div([
                    dcc.Dropdown(
                        options=[x for x in sorted(list_names)],
                        multi=True,
                        id='my_txt_input'

                    )
                ],
                    className="input_box1",
                )],
                className="athl1_zone",
            ),
            html.Datalist(id='Nom_athl'),

            # Selection Athlète #2
            html.Div([
                html.Div(
                    children=[
                        html.P("Athlète #2")
                    ],
                    id='athl2_info',
                    className="athl2_box",
                ),
                html.Div([
                    dcc.Input(
                        id='my_txt_input2',
                        value='',
                        type='text',
                        debounce=True,  # changes to input are sent to Dash server only on enter or losing focus
                        pattern=r"^[A-Za-z].*",  # Regex: string must start with letters only
                        spellCheck=True,
                        inputMode='latin',
                        # provides a hint to browser on type of data that might be entered by the user.
                        name='text',  # the name of the control, which is submitted with the form data
                        list='Nom_athl',  # identifies a list of pre-defined options to suggest to the user
                        n_submit=0,  # number of times the Enter key was pressed while the input had focus
                        n_submit_timestamp=-1,  # last time that Enter was pressed
                        autoFocus=True,  # the element should be automatically focused after the page loaded
                        n_blur=0,  # number of times the input lost focus
                        n_blur_timestamp=-1,  # last time the input lost focus.

                        # Dynamically generate options
                        # selectionDirection='', # the direction in which selection occurred
                        # selectionStart='',     # the offset into the element's text content of the first selected character
                        # selectionEnd='',       # the offset into the element's text content of the last selected character
                    )
                ],
                    className="input_box2",
                )],
                className="athl2_zone",
            ),
            html.Datalist(id='Nom_athl2'),
        ],
            className="athl_zone",
        ),

        html.Div([
            html.Div([
                html.P("")
            ],
                id="athlete1_nom",
                className="athl1_nom"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete1_club",
                className="athl1_club"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete1_anniv",
                className="athl1_anniv"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete1_max",
                className="athl1_max"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete1_total",
                className="athl1_total"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete1_pdc",
                className="athl1_pdc"
            )
        ],
            id="athlete1_info",
            className="athl1_info"
        ),

        html.Div([
            html.Div([
                html.P("")
            ],
                id="athlete2_nom",
                className="athl2_nom"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete2_club",
                className="athl1_club"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete2_anniv",
                className="athl2_anniv"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete2_max",
                className="athl2_max"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete2_total",
                className="athl2_total"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete2_pdc",
                className="athl2_pdc"
            )
        ],
            id="athlete2_info",
            className="athl2_info"
        ),

        html.Div([
            html.Div([
                html.P("")
            ],
                id="athlete3_nom",
                className="athl3_nom"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete3_club",
                className="athl1_club"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete3_anniv",
                className="athl3_anniv"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete3_max",
                className="athl3_max"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete3_total",
                className="athl3_total"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete3_pdc",
                className="athl3_pdc"
            )
        ],
            id="athlete3_info",
            className="athl3_info"
        ),

        html.Div([
            html.Div([
                html.P("")
            ],
                id="athlete4_nom",
                className="athl4_nom"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete4_club",
                className="athl1_club"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete4_anniv",
                className="athl4_anniv"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete4_max",
                className="athl4_max"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete4_total",
                className="athl4_total"
            ),
            html.Div([
                html.P("")
            ],
                id="athlete4_pdc",
                className="athl4_pdc"
            )
        ],
            id="athlete4_info",
            className="athl4_info"
        ),
    ],
        className="filter_zone",
    ),

    html.Br(),
    html.Div([
        dcc.Graph(id='graph-with-slider'),
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
    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
            columns=[
                {"name": i, "id": i, "selectable": True} for i in
                ['Nom', 'Competition', 'Date', 'PdC', 'Arr1', 'Arr2', 'Arr3', 'EpJ1', 'EpJ2', 'EpJ3', 'Total', 'Série',
                 'Catégorie', 'IWF']
            ],
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="single",
            column_selectable="single",
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'text-align': 'left',
                'text-indent': '0.2em'
            },
            style_data={
                'backgroundColor': 'rgb(80, 80, 90)',
                'color': 'white',
                'border': '1px solid white'
            },
            row_selectable="multi",
            row_deletable=False,
            selected_columns=[],
            selected_rows=[],
            style_as_list_view=True,
            page_action="native",
            page_current=0,
            page_size=25,
        ),
    ], className='data_tab'),
    html.Div(id='datatable-interactivity-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/01_dash_board.css'
    ),
    html.Div(id='none', children=[], style={'display': 'none'})
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
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF',
        'color': '#202020'
    } for i in selected_columns]


@callback(
    Output('my_txt_input', 'options'),
    Input('year-slider', 'value'),
    prevent_initial_call=True
)
def update_athletes_list(selected_year):
    filtered_df = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    options = list(set(filtered_df['Nom'].tolist()))
    return options


# @callback(
#    Output('datatable-interactivity-container', "children"),
#    Input('datatable-interactivity', "derived_virtual_data"),
#    Input('datatable-interactivity', "derived_virtual_selected_rows"))


@callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])
def update_figure(selected_year, txt_inserted):
    if selected_year == '':
        selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
    filtered_df = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if txt_inserted:
        filtered_df = filtered_df[(filtered_df['Nom'].isin(txt_inserted))]
    else:
        filtered_df = filtered_df[(filtered_df['Nom'] == 'Camille MOUNIER')]

    fig = px.scatter(filtered_df, x="Mois", y="IWF", hover_name="Competition", color="Nom", log_x=False, size_max=55)
    fig.update_traces(marker=dict(size=10, symbol='circle'))
    fig.update_xaxes(categoryorder="category ascending")
    fig.update_yaxes(categoryorder="category ascending")
    fig.update_layout(transition_duration=5, plot_bgcolor='rgb(40,40,45)', paper_bgcolor='rgb(40,40,45)',
                      font_color="white",
                      title_font_color="white", legend_title_font_color="white")

    return fig


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
        filtered_df = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (
                    df['SaisonAnnee'] <= max(selected_year))]
    else:
        filtered_df = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

    columns = [
        {"name": i, "id": i, "selectable": True} for i in
        ['Nom', 'Competition', 'Date', 'PdC', 'Arr1', 'Arr2', 'Arr3', 'EpJ1', 'EpJ2', 'EpJ3', 'Total', 'Série',
         'Catégorie', 'IWF']
    ]

    dat = filtered_df.to_dict('records')

    return dat, columns


# @callback(
#    Output("filter_info", "children"),
#    [Input('year-slider', 'value'),
#    Input(component_id='my_txt_input', component_property='value')
#    ])


# def update_title(selected_year, txt_inserted):
#     # Perform any manipulation on input_value and return the updated title
#     global updated_title
#     if min(selected_year)==max(selected_year):
#         year_text = 'Saison ' + str(max(selected_year))
#     else:
#         year_text = 'Saisons ' + str(min(selected_year)) + '/' + str(max(selected_year))
#
#     if txt_inserted:
#         df_filtered = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year) & (df['SaisonAnnee'] <= max(selected_year)))]
#         df1 = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
#
#     if ((not txt_inserted) or len(df_filtered )==0):
#         updated_title = "Haltero Data"
#     elif (len(df1)!=0):
#         updated_title = f"{txt_inserted}\n{year_text}"
#
#     return updated_title


@callback(
    [Output("athlete1_nom", "children"),
     Output("athlete1_club", "children"),
     Output("athlete1_anniv", "children"),
     Output("athlete1_max", "children"),
     Output("athlete1_total", "children"),
     Output("athlete1_pdc", "children"),
     Output("athlete2_nom", "children"),
     Output("athlete2_club", "children"),
     Output("athlete2_anniv", "children"),
     Output("athlete2_max", "children"),
     Output("athlete2_total", "children"),
     Output("athlete2_pdc", "children"),
     Output("athlete3_nom", "children"),
     Output("athlete3_club", "children"),
     Output("athlete3_anniv", "children"),
     Output("athlete3_max", "children"),
     Output("athlete3_total", "children"),
     Output("athlete3_pdc", "children"),
     Output("athlete4_nom", "children"),
     Output("athlete4_club", "children"),
     Output("athlete4_anniv", "children"),
     Output("athlete4_max", "children"),
     Output("athlete4_total", "children"),
     Output("athlete4_pdc", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])
def updated_athletes(selected_year, txt_inserted):
    # Perform any manipulation on input_value and return the updated title
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
    for i in txt_inserted:
        print(str(min(selected_year)) + ' ' + i)
        updated_name[n] = i
        df1 = df[
            (df['Nom'] == i) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

        if len(df1['Club'].values[0]) > 21:
            updated_club[n] = df1['Club'].values[0][0:20] + '.'
        else:
            updated_club[n] = df1['Club'].values[0]
        updated_anniv[n] = df1['Né le'].values[0]
        updated_max[n] = str(df1['IWF'].max()) + ' IWF'
        updated_arr[n] = str(df1['Arraché'].max()) + '/'
        updated_epj[n] = str(df1['EpJeté'].max()) + '/'
        updated_total[n] = df1['Total'].max()
        pdc_df = df1['Total'].idxmax()
        updated_pdc[n] = str(df.loc[pdc_df, 'PdC']) + ' PdC'
        n = n + 1

    return f"{updated_name[0]}", f"{updated_club[0]}", f"{updated_anniv[0]}", f"{updated_max[0]}", f"{updated_arr[0]}{updated_epj[0]}{updated_total[0]}", f"{updated_pdc[0]}", \
        f"{updated_name[1]}", f"{updated_club[1]}", f"{updated_anniv[1]}", f"{updated_max[1]}", f"{updated_arr[1]}{updated_epj[1]}{updated_total[1]}", f"{updated_pdc[1]}", \
        f"{updated_name[2]}", f"{updated_club[2]}", f"{updated_anniv[2]}", f"{updated_max[2]}", f"{updated_arr[2]}{updated_epj[2]}{updated_total[2]}", f"{updated_pdc[2]}", \
        f"{updated_name[3]}", f"{updated_club[3]}", f"{updated_anniv[3]}", f"{updated_max[3]}", f"{updated_arr[3]}{updated_epj[3]}{updated_total[3]}", f"{updated_pdc[3]}",


if __name__ == '__main__':
    run_server(debug=True)
