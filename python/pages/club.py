import dash
import plotly.express as px
from dash import dash_table, dcc, html, callback
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
            ,   cat.PoidsTotal      as "Total"
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

df['Max IWF Saison']=round(df['Max IWF Saison'], 3)
df['Max IWF']=round(df['Max IWF'], 3)

dfh = df
dff = df
dfh['Rang'] = df[(df['Sexe'] == 'M') & df['SaisonAnnee'] == max(df['SaisonAnnee'])].groupby(['SaisonAnnee']).cumcount() + 1
dff['Rang'] = df[(df['Sexe'] == 'F') & df['SaisonAnnee'] == max(df['SaisonAnnee'])].groupby(['SaisonAnnee']).cumcount() + 1

updated_title='Dashboard Club'

#app = dash.Dash(__name__)
dash.register_page(__name__)
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
                    id='my_txt_input1-c',
                    placeholder="Ligue",
                )
            ], xs=6, sm=6, md=6, lg=5, xl=5),
            dbc.Col([
                dcc.Dropdown(
                    options=[x for x in sorted(nom_club)],
                    multi=True,
                    id='my_txt_input2-c',
                    placeholder="Club"
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
    html.Div([
        ],
        id='div_output',
        className='graph_box'
    ),


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
    Output('my_txt_input2-c', 'options'),
    [Input('year-slider', 'value'),
     Input('my_txt_input1-c', 'value')]
)

def update_datalist(selected_year, txt_inserted1):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    filtered_df = df[(df['SaisonAnnee'] == selected_year)]
    if txt_inserted1:
        filtered_df = filtered_df[(filtered_df['Ligue'].isin(txt_inserted1))]

    nom_club = list(set(filtered_df['Club'].tolist()))
    opt = [x for x in sorted(nom_club)]
    return opt

@callback(
    [Output('datatable-h', "data"),
     Output('datatable-h', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input1-c', component_property='value'),
     Input(component_id='my_txt_input2-c', component_property='value')
     ])

def update_data(selected_year=None, txt_inserted=None, txt_inserted2=None):
    fdfh = df[(df['Sexe'] == 'M')]
    if selected_year == '':
        selected_year = fdfh['SaisonAnnee'].max()
    if txt_inserted or txt_inserted2:
        if txt_inserted:
            fdfh = fdfh[(fdfh['Ligue'].isin(txt_inserted)) & (fdfh['SaisonAnnee'] == selected_year)]
        if txt_inserted2:
            fdfh = fdfh[(fdfh['Club'].isin(txt_inserted2)) & (fdfh['SaisonAnnee'] == selected_year)]
    else:
        fdfh = fdfh[(fdfh['SaisonAnnee'] == selected_year)]

    fdfh=fdfh.sort_values(by=['Max IWF Saison'], ascending=False)
    fdfh['Rang'] = fdfh.groupby(['SaisonAnnee']).cumcount()+1
    columns = [
            {"name": i, "id": i,  "selectable": True} for i in
            ['Rang', 'Nom', 'Arr', 'EpJ', 'Tot', 'PdC', 'IWF']
    ]

    dat = fdfh.to_dict('records')

    return dat, columns

@callback(
    [Output('datatable-f', "data"),
     Output('datatable-f', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input1-c', component_property='value'),
     Input(component_id='my_txt_input2-c', component_property='value')
     ])

def update_data(selected_year, txt_inserted, txt_inserted2):
    fdff = df[(df['Sexe'] == 'F')]
    if selected_year == '':
        selected_year = fdff['SaisonAnnee'].max()
    if txt_inserted or txt_inserted2:
        if txt_inserted:
            fdff = fdff[(fdff['Ligue'].isin(txt_inserted)) & (fdff['SaisonAnnee'] == selected_year)]
        if txt_inserted2:
            fdff = fdff[(fdff['Club'].isin(txt_inserted2)) & (fdff['SaisonAnnee'] == selected_year)]
    else:
        fdff = fdff[(fdff['SaisonAnnee'] == selected_year)]

    fdff=fdff.sort_values(by=['Max IWF Saison'], ascending=False)
    fdff['Rang'] = fdff.groupby(['SaisonAnnee']).cumcount()+1

    columns = [
            {"name": i, "id": i,  "selectable": True} for i in
            ['Rang', 'Nom', 'Arr', 'EpJ', 'Tot', 'PdC', 'Max IWF Saison']
    ]

    dat = fdff.to_dict('records')

    return dat, columns

@callback(
    Output("top_5_h", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input1-c', component_property='value'),
     Input(component_id='my_txt_input2-c', component_property='value')
     ])

def update_title(selected_year, txt_inserted, txt_inserted2):
    # Perform any manipulation on input_value and return the updated title
    global updated_title_h
    fdfh = df[(df['Sexe'] == 'M')]
    if selected_year=='':
        selected_year=fdfh['SaisonAnnee'].max()
    if txt_inserted or txt_inserted2:
        if txt_inserted:
            fdfh = fdfh[(fdfh['Ligue'].isin(txt_inserted)) & (fdfh['SaisonAnnee'] == selected_year)]
        if txt_inserted2:
            fdfh = fdfh[(fdfh['Club'].isin(txt_inserted2)) & (fdfh['SaisonAnnee'] == selected_year)]
    else:
        fdfh = fdfh[(fdfh['SaisonAnnee'] == selected_year)]

    fdfh=fdfh.sort_values(by=['Max IWF Saison'], ascending=False)
    filtered_df=round(fdfh.head(5),0)
    res = filtered_df['Max IWF Saison'].sum()
    updated_title_h = "Top 5 Hommes : " + str(int(res))

    return updated_title_h

@callback(
    Output("top_5_f", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input1-c', component_property='value'),
     Input(component_id='my_txt_input2-c', component_property='value')
     ])

def update_title(selected_year, txt_inserted, txt_inserted2):
    # Perform any manipulation on input_value and return the updated title
    global updated_title_f
    fdff = df[(df['Sexe'] == 'F')]
    if selected_year == '':
        selected_year = fdff['SaisonAnnee'].max()
    if txt_inserted or txt_inserted2:
        if txt_inserted:
            fdff = fdff[
                (fdff['Ligue'].isin(txt_inserted)) & (fdff['SaisonAnnee'] == selected_year)]
        if txt_inserted2:
            fdff = fdff[
                (fdff['Club'].isin(txt_inserted2)) & (fdff['SaisonAnnee'] == selected_year)]
    else:
        fdff = fdff[(fdff['SaisonAnnee'] == selected_year)]

    fdff = fdff.sort_values(by=['Max IWF Saison'], ascending=False)
    filtered_df=round(fdff.head(4),0)
    res = filtered_df['Max IWF Saison'].sum()
    updated_title_f = "Top 4 Femmes : " + str(int(res))

    return updated_title_f


if __name__ == '__main__':
    run_server(debug=True)
