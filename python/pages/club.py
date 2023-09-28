import dash
import plotly.express as px
from dash import dash_table, dcc, html, callback
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
import numpy as np
import os
from dash.dependencies import Input, Output
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
            ,   apr.MaxIWFSaison    as "Max IWF Saison"
            ,   apr.MaxIWF          as "Max IWF"
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
    html.Div([
        # Titre
        html.Div(
            children=[
                html.P("Dashboard Clubs")
            ],
            id='filter_info',
            className="text-box",
        ),
        # Zone filtres Ligue / Club
        html.Div([
            html.Div([
                # Selection Ligue
                html.Div(
                    children=[
                        html.P("Ligue")
                    ],
                    id='ligue_info',
                    className="ligue_box",
                ),
                html.Div([
                        dcc.Input(
                            id='my_txt_input',
                            value='',
                            type='text',
                            debounce=True,  # changes to input are sent to Dash server only on enter or losing focus
                            pattern=r"^[A-Za-z].*",  # Regex: string must start with letters only
                            spellCheck=True,
                            inputMode='latin',  # provides a hint to browser on type of data that might be entered by the user.
                            name='text',  # the name of the control, which is submitted with the form data
                            list='list_ligues',  # identifies a list of pre-defined options to suggest to the user
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
                    className="input_box1",
                )] ,
                className="ligue_zone",
            ),
            html.Datalist(id='list_ligues'),

            #Selection Athlète #2
            html.Div([
                html.Div(
                    children=[
                        html.P("Club")
                    ],
                    id='club_info',
                    className="club_box",
                ),
                html.Div([
                    dcc.Input(
                        id='my_txt_input2',
                        value='',
                        type='text',
                        debounce=True,  # changes to input are sent to Dash server only on enter or losing focus
                        pattern=r"^[A-Za-z].*",  # Regex: string must start with letters only
                        spellCheck=True,
                        inputMode='latin',  # provides a hint to browser on type of data that might be entered by the user.
                        name='text',  # the name of the control, which is submitted with the form data
                        list='list_clubs',  # identifies a list of pre-defined options to suggest to the user
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
                className="club_zone",
            ),
            html.Datalist(id='list_clubs'),
            ],
        className="pick_zone",
        )],
    ),
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
    html.Div([
        html.Div(children=[
                html.P("Top 5 Hommes : ")
                ],
                 id='top_5_score_h',
                 className='top_5_h'),
        html.Div(children=[
                html.P("Top 4 Femmes : ")
                ],
                 id='top_5_score_f',
                className='top_5_f'),
            ],
    className = 'top_5'),

    html.Div([
        html.Div([
            dash_table.DataTable(
                id='datatable-h',
                # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
                    columns=[
                        {"name": i, "id": i,  "selectable": True} for i in
                        ['Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'Max IWF Saison']
                ],
                data=df[(df['Sexe'] == 'M')].to_dict('records'),
                editable=True,
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
                row_selectable=False,
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                style_as_list_view=True,
                page_action="native",
                page_current=0,
                page_size=25,
            ),
        ], className='data_tab_h'),
        html.Div([
            dash_table.DataTable(
                id='datatable-f',
                # tab_selected_columns=['Nom', 'Né le','Competition','PdC', 'Arrache','EpJete','Total','IWF'],
                    columns=[
                        {"name": i, "id": i,  "selectable": True} for i in
                        ['Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'Max IWF Saison']
                ],
                data=df[(df['Sexe'] == 'F')].to_dict('records'),
                editable=True,
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
                row_selectable=False,
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                style_as_list_view=True,
                page_action="native",
                page_current=0,
                page_size=25,
            ),
        ], className='data_tab_f'),
    ], className='data_tabs'),
    html.Div(id='datatable-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/02_club.css'
        ),
    html.Div(id='none',children=[],style={'display': 'none'})
    ],
    id='app_code',
    className='body'
)


@callback(
    Output('list_ligues', 'children'),
    [Input('none', 'children')]
)
def update_datalist(none):
    children = []  # List to store dynamic options

    children = [html.Option(value=val, children=val) for val in nom_ligue]

    return children

@callback(
    Output('list_clubs', 'children'),
    [Input('none', 'children')]
)
def update_datalist(none):
    children = []  # List to store dynamic options

    children = [html.Option(value=val, children=val) for val in nom_club]

    return children

@callback(
    [Output('datatable-h', "data"),
     Output('datatable-h', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_data(selected_year=None, txt_inserted=None, txt_inserted2=None):
    filtered_df = df[(df['Sexe'] == 'M')]
    if selected_year=='':
        selected_year=filtered_df['SaisonAnnee'].max()
    if txt_inserted + txt_inserted2 != '':
        if txt_inserted!='':
            filtered_df = filtered_df[(filtered_df['Ligue'] == txt_inserted) & (filtered_df['SaisonAnnee'] == selected_year)]
        if txt_inserted2!='':
            filtered_df = filtered_df[(filtered_df['Club'] == txt_inserted2) & (filtered_df['SaisonAnnee'] == selected_year)]
    else:
        filtered_df = filtered_df[(filtered_df['SaisonAnnee'] == selected_year)]

    filtered_df=filtered_df.sort_values(by=['Max IWF Saison'], ascending=False)
    columns = [
            {"name": i, "id": i,  "selectable": True} for i in
            ['Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'Max IWF Saison']
    ]

    dat = filtered_df.to_dict('records')

    return dat, columns

@callback(
    [Output('datatable-f', "data"),
     Output('datatable-f', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_data(selected_year=None, txt_inserted=None, txt_inserted2=None):
    filtered_df = df[(df['Sexe'] == 'F')]
    if selected_year=='':
        selected_year=filtered_df['SaisonAnnee'].max()
    if txt_inserted + txt_inserted2 != '':
        if txt_inserted != '':
            filtered_df = filtered_df[(filtered_df['Ligue'] == txt_inserted) & (filtered_df['SaisonAnnee'] == selected_year)]
        if txt_inserted2 != '':
            filtered_df = filtered_df[(filtered_df['Club'] == txt_inserted2) & (filtered_df['SaisonAnnee'] == selected_year)]
    else:
        filtered_df = filtered_df[(filtered_df['SaisonAnnee'] == selected_year)]

    filtered_df=filtered_df.sort_values(by=['Max IWF Saison'], ascending=False)
    columns = [
            {"name": i, "id": i,  "selectable": True} for i in
            ['Nom', 'Arr', 'EpJ', 'Total', 'PdC', 'Max IWF Saison']
    ]

    dat = filtered_df.to_dict('records')

    return dat, columns

@callback(
    Output("top_5_score_h", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_title(selected_year, txt_inserted, txt_inserted2):
    # Perform any manipulation on input_value and return the updated title
    global updated_title
    filtered_df = df[(df['Sexe'] == 'M')]
    if selected_year=='':
        selected_year=df['SaisonAnnee'].max()
    if txt_inserted + txt_inserted2 != '':
        if txt_inserted != '':
            filtered_df = filtered_df[(df['Ligue'] == txt_inserted) & (filtered_df['SaisonAnnee'] == selected_year)]
        if txt_inserted2 != '':
            filtered_df = filtered_df[(filtered_df['Club'] == txt_inserted2) & (filtered_df['SaisonAnnee'] == selected_year)]
    else:
        filtered_df = df[(df['SaisonAnnee'] == selected_year)]

    filtered_df=filtered_df.sort_values(by=['Max IWF Saison'], ascending=False)
    filtered_df=round(filtered_df.head(5),0)
    res = filtered_df['Max IWF Saison'].sum()
    updated_title = "Top 5 Hommes : " + str(int(res))

    return updated_title

@callback(
    Output("top_5_score_f", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_title(selected_year, txt_inserted, txt_inserted2):
    # Perform any manipulation on input_value and return the updated title
    global updated_title
    filtered_df = df[(df['Sexe'] == 'F')]
    if selected_year=='':
        selected_year=df['SaisonAnnee'].max()
    if txt_inserted + txt_inserted2 != '':
        if txt_inserted!='':
            filtered_df = filtered_df[(df['Ligue'] == txt_inserted) & (filtered_df['SaisonAnnee'] == selected_year)]
        if txt_inserted2!='':
            filtered_df = filtered_df[(filtered_df['Club'] == txt_inserted2) & (filtered_df['SaisonAnnee'] == selected_year)]

    filtered_df=filtered_df.sort_values(by=['Max IWF Saison'], ascending=False)
    filtered_df=round(filtered_df.head(4),0)
    res = filtered_df['Max IWF Saison'].sum()
    updated_title = "Top 4 Femmes : " + str(int(res))

    return updated_title


if __name__ == '__main__':
    run_server(debug=True)
