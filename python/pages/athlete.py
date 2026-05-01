import dash
import plotly.express as px
from dash import dcc, callback, State, html, clientside_callback
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
import dash_ag_grid as dag
import os
from dash.dependencies import Input, Output
import dash_daq as daq
import dash_bootstrap_components as dbc
import time

# Connection à la base SQLite

print("full start: " + str(time.time()))
dirname = os.path.dirname(__file__)
path_db = os.path.join(dirname, 'dataltero.db')
conn = sql.connect(database=path_db)
print("db conn : " + str(time.time()))

# Requête principale
qry = "SELECT * FROM REPORT_ATHLETES"
df = pd.read_sql_query(qry, conn)
df.head()


print("qry 1 done : " + str(time.time()))

# Requête secondaire pour le détail athlète
qry2 = """SELECT ath.Nom, cat.Serie as "Série", cat.Categorie as "Catégorie"
      FROM ATHLETE as ath 
      LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
      LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
      LEFT JOIN CLUB as clb on clb.Club = cat.CATClub"""
df2 = pd.read_sql_query(qry2, conn)
df2.head()

# Requête
qry3 = """SELECT max(cmp.DateCompet) as "Date"
      FROM COMPET as cmp """
df3 = pd.read_sql_query(qry3, conn)
df3.head()

print("qry done : " + str(time.time()))

# Reformatage des donnée de la requête
df['IWF'] = round(df['IWF'], 3)
df['MoisCompet'] = pd.Categorical(df['MoisCompet'], ["08", "09", "10", "11", "12", "01", "02", "03", "04", "05", "06", "07"])
df2['Série'] = pd.Categorical(df2['Série'], ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "HON", "NAT", "INT B", "EUR", "INT A", "MON", "OLY"], ordered=True)
df_temp = df[df['Nom']=='ZZZZZ']
dash.register_page(__name__, path='/', name='3PR - Athletes', title='3PR - Perfs Athlètes', image='/assets/3PR.png', description='Tableau de bord des performances des haltérophiles français')

# Liste d'athlètes = ceux qui ont tiré sur la plage par défaut càd l'année dernière + l'année en cours
selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
list_names = list(set(df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]['Nom'].tolist()))

# body
layout = html.Div([
    # Header & filtres

        dbc.Row([
            html.P("MàJ : " + df3.iloc[0,0], id="zone_news", className="news")
        ]),
        dbc.Row([            # Titre
            dbc.Col([
                dbc.Button(" Dashboard Athlètes ", id="title-box", color="danger", className="titlebox", size="md"),
                    dbc.Modal([
                        dbc.ModalHeader(" Perfs Athlètes ", id="athlete_info_"),
                        dbc.ModalBody([
                            html.Div([html.P("Cette page...")]),
                        ]),
                        dbc.ModalFooter(
                            dbc.Button("Fermer", id="close-athlete_info-", color="secondary", className="ml-auto")
                        ),
                    ], id="athlete-info-modal_", size="lg", centered=True, is_open=False),
                ], xs=6, sm=6, md=6, lg=2, xl=2),

            # Zone filtres athlètes
            dbc.Col([
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            options=[x for x in sorted(list_names)],
                            multi=True,
                            id='my_txt_input',
                            placeholder="Choisir des athlètes...",
                            className="input_box1",
                            value=''
                            )
                        ]),
                    #html.Datalist(id='Nom_athl')
                    ])
                ], xs=6, sm=6, md=6, lg=2, xl=2),

            # Cartes athlètes (masquées par défaut)
            dbc.Col([
                html.Div([
                    dbc.Card(
                        dbc.CardBody([
                                html.Div([html.P("Card 1")], id="athlete1_nom", className="card-title"),
                                html.Div([
                                    html.Div([html.P("Club")], id="athlete1_club"),
                                    html.Div([html.P("NaissanceMax")], id="athlete1_annivmax")
                                  ],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl1", color="danger", className="mt-auto", size="sm"),

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
                                    html.Div([html.P("NaissanceMax")], id="athlete2_annivmax")],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl2", color="primary", className="mt-auto", size="sm"),
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
                                    html.Div([html.P("NaissanceMax")], id="athlete3_annivmax")],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl3", color="warning", className="mt-auto", size="sm"),
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
                                    html.Div([html.P("NaissanceMax")], id="athlete4_annivmax")],   className="card-text",
                                ),
                                dbc.Button("+ Info", id="open_athl4", color="success", className="mt-auto", size="sm"),
                                dbc.Modal([
                                    dbc.ModalHeader([
                                        dbc.ModalTitle("Information", id="athlete_nom_info", class_name='ath_info_header'),
                                        html.Div([
                                            dbc.Row([
                                                dbc.Col([
                                                    dbc.Button("❓", id="open-aide_achievements-athl", color="white", className="mt-auto", size="sm"),
                                                    dbc.Modal([
                                                        dbc.ModalHeader([
                                                            dbc.ModalTitle("Information", id="achievement_aide_header_athl"),
                                                        ]),
                                                        dbc.ModalBody([
                                                            html.P("", id="ach_aide-txt_athl"),
                                                            html.Div(id="ach_aide-table_athl"),
                                                        ]),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Fermer", id="close-aide_achievements-athl", color="secondary", className="ml-auto")
                                                        ),
                                                    ], id="aide_achievements_athl", size="md", centered=True, is_open=False),
                                                ]),
                                            ], align="right"),
                                        ], id='ach_aide-div_athl', style= {'display': 'none'})
                                    ], close_button=False),
                                    dbc.ModalBody([
                                        dbc.Button("Voir les Athlètes Similaires", id="athl_sim", color="primary", className="mt-auto", size="sm"),
                                        html.Div(id="athl_sim-table", className="athl_data_tab", style = {'display': 'none'}),
                                        dcc.Graph(id='athl-graph', style = {'display': 'none'}),
                                        html.Div(id="athl-table", className="athl_data_tab"),
                                    ]),
                                    dbc.ModalFooter(
                                        dbc.Button("Fermer", id="close-athl", color="secondary", className="ml-auto")
                                    ),
                                ], id="athl-modal", size="lg", centered=True, is_open=False, scrollable=True),
                            ]
                        ),
                    )
                ], id="athl_card4",  style= {'display': 'none'}),
            ], xs=6, sm=3, md=3, lg=2, xl=2),
        ],  className="top_zone",),


    print("a"),
    # Zone graph
    html.Br(),
    dbc.Row([
        dbc.Col([
            daq.BooleanSwitch(id='bool_total',
                              on=False,
                              label={"label": "IWF/Total", 'style': {"color": "white", "font-size": "10"}},
                              labelPosition="bottom",
                              color="#DC3545"),
        ], xs=6, sm=3, md=2, lg=2, xl=1),
        dbc.Col([
            dbc.Button("↪️", id="reset_col", color="light", outline=True, className="mt-auto", size="sm"),
            dbc.Button("💾", id="excel_export", color="light", outline=True, className="mt-auto", size="sm"),
        ],  className="boutons", xs=6, sm=3, md=2, lg=2, xl=1),
        dbc.Col([
            dcc.RangeSlider(
                df['SaisonAnnee'].min(),
                df['SaisonAnnee'].max(),
                step=None,
                value=selected_year,
                marks={str(year): {'label' : str(year), 'style':{'color':'white'}} for year in df['SaisonAnnee'].unique()},
                id='year-slider-athl',
                className='slider_zone'
                ),
            ], xs=12, sm=6, md=8, lg=8, xl=10),
    ]),

    # Zone data table AG Grid
    html.Br(),
    html.Div([
        dag.AgGrid(
            id = "ag_datatable_athl",
            enableEnterpriseModules=True,
            rowData = df_temp.to_dict("records"),
            columnDefs = [
                        {
                            "headerName": "Athlete",
                            "children": [
                                {"field": "Nom", "width": 200, "pinned": "left", "hide": False},
                            ],
                        },
                        {
                            "headerName": "Arraché",
                            "children": [
                                {"field": "Arr1", "headerName": "1", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "Arr2", "headerName": "2", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "Arr3", "headerName": "3", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "Arr", "width": 75, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(235, 61, 85)'} : {'color': 'rgb(59, 113, 202)'}",
                                 },
                                 },
                            ],
                        },
                        {
                            "headerName": "Epaulé Jeté", "hide": False,
                            "children": [
                                {"field": "EpJ1", "headerName": "1", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "EpJ2", "headerName": "2", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "EpJ3", "headerName": "3", "width": 60, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(220, 76, 100)'} : {'color': 'rgb(20, 164, 77)'}",
                                 },
                                 },
                                {"field": "EpJ", "width": 75, "hide": False,
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(235, 61, 85)'} : {'color': 'rgb(59, 113, 202)'}",
                                 },
                                 },
                            ],
                        },
        
                        {
                            "headerName": "Performance",
                            "children": [
                                {"field": "Total", "width": 80, "hide": False, "font-weight": 'bold',
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {'color': 'rgb(255, 41, 65)'} : {'color': 'rgb(44, 98, 217)'}",
                                 },
                                 },
                                {"field": "IWF", "width": 80, "hide": False, "valueFormatter": {"function": "params.value ? params.value.toFixed(3) : ''"}},
                                {"field": "Série", "width": 80, "hide": False},
                                {"field": "PdC", "width": 80, "hide": False, "valueFormatter": {"function": "params.value ? params.value.toFixed(2) : ''"}},
                                {"field": "Catégorie", "width": 100, "hide": False},
                            ],
                        },
                        {
                            "headerName": "Compétition",
                            "children": [
                                {"field": "Date", "width": 150, "hide": False},
                                {"field": "Competition", "hide": False}
                            ],
                        }
                    ],
            defaultColDef = {"resizable": True, "sortable": True, "filter": True},
            suppressDragLeaveHidesColumns=True,
            dashGridOptions = {"pagination": False},
            className = "ag-theme-quartz-dark",  # https://dashaggrid.pythonanywhere.com/layout/themes
        )

    ]),

    dbc.Col([
        dcc.Graph(
            id='graph-with-slider',
            style={'display': 'none'}
        ),
    ], width=12),

    html.Br(),
    html.Br(),
    html.Link(
        rel='stylesheet',
        href='/assets/01_dash_board.css'
    )
    ],
    id='app_code_athl',
    className='body'
)

print("end page load : " + str(time.time()))


# Mise à jour de la liste d'athlète dispo en fonction des années de référence
@callback(
    Output('my_txt_input', 'options'),
    Input('year-slider-athl', 'value'),
    prevent_initial_call=True
)

def update_athletes_list(selected_year):
    fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    list_names = list(set(fdf['Nom'].tolist()))
    options = [x for x in sorted(list_names)]
    return options

#Mise à jour du graphique
@callback(
    [Output('graph-with-slider', 'figure'),
     Output('graph-with-slider', 'style')],
    [Input('year-slider-athl', 'value'),
     Input('bool_total', 'on'),
     Input('bool_light', 'on'),
     Input('my_txt_input', 'value'),
     Input("reset_col", "n_clicks"),
     Input("display", "children")
     ],
     prevent_initial_call=True)

def update_figure(selected_year, on, on_light, txt_inserted, n_clicks, breakpoint_str):
    if selected_year == '':
        selected_year = [df['SaisonAnnee'].max() - 1, df['SaisonAnnee'].max()]
    fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if txt_inserted:
        # On trie par nom pour aligner la saisie, les cartes et le graphique
        fdf = fdf[(fdf['Nom'].isin(txt_inserted))]
        fdf.Nom = fdf.Nom.astype("category")
        fdf.Nom = fdf.Nom.cat.set_categories(txt_inserted)
        fdf = fdf.sort_values(by='Nom')
        if breakpoint_str=="md":
            display_graph = {'display': 'block', 'height': 300}
        else:
            display_graph = {'display': 'block', 'height': '50vh'}

        if on_light == True:
            font_col = 'rgb(40,40,45)'
            plot_col = 'rgb(249, 250, 251)'
        else:
            font_col = "white"
            plot_col = 'rgb(40,40,45)'

        #Paramètres de graph
        if on_light == True:
            color_seq = ["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#282D2D", "purple", "#54B4D3", "#9FA6B2"]
        else:
            color_seq = ["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple", "#54B4D3", "#9FA6B2"]

        if on == True:
            fig = px.scatter(fdf, x="Date", y="Total",  hover_name="Competition", hover_data=["Arr", "EpJ", "PdC", "Série"],
                                      color="Nom", log_x=False, size_max=55,color_discrete_sequence=color_seq, )
        else:
            fig = px.scatter(fdf, x="Date", y="IWF",  hover_name="Competition", hover_data=["Arr", "EpJ", "PdC", "Série"],
                                      color="Nom", log_x=False, size_max=55,color_discrete_sequence=color_seq, )
        fig.update_traces(marker=dict(size=10, symbol='circle'))

        fig.update_xaxes(categoryorder="category ascending", gridcolor='LightGrey')
        fig.update_yaxes(categoryorder="category ascending", gridcolor='LightGrey')
        fig.update_layout(transition_duration=5, plot_bgcolor=plot_col, paper_bgcolor=plot_col,
                          font_color=font_col, font_size=12,
                          title_font_color=font_col, legend_title_font_color=font_col,
                          legend=dict(
                              orientation="h",
                              yanchor="bottom",
                              y=1.05,
                              xanchor="left",
                              x=-0.05
                            )
                          )
    else:
        fig = px.scatter()
        display_graph = {'display': 'none'}
    return fig, display_graph

# Mise à jour data table
@callback(
    [Output('ag_datatable_athl', 'rowData')],
    [Input('year-slider-athl', 'value'),
     Input('bool_total', 'on'),
     Input('my_txt_input', 'value')],
     )

def update_data_ag(selected_year, on, txt_inserted):
    if selected_year == '':
        selected_year = df['SaisonAnnee'].max()
    if txt_inserted:
        fdf = df[df['Nom'].isin(txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    else:
        fdf = df[(df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    if on == True:
        fdf = fdf.sort_values(by=['Total'], ascending=False)
    else:
        fdf = fdf.sort_values(by=['IWF'], ascending=False)
    dat_ag = fdf.to_dict('records')
    print("b")
    return [dat_ag]

# Génération des cartes des 4 premiers athlètes
@callback(
    [Output('athl_card1', 'style'),
     Output("athlete1_nom", "children"),
     #Output("athlete1_achievements", "children"),
     Output("athlete1_club", "children"),
     Output("athlete1_annivmax", "children"),
     Output('athl_card2', 'style'),
     Output("athlete2_nom", "children"),
     #Output("athlete2_achievements", "children"),
     Output("athlete2_club", "children"),
     Output("athlete2_annivmax", "children"),
     Output('athl_card3', 'style'),
     Output("athlete3_nom", "children"),
     #Output("athlete3_achievements", "children"),
     Output("athlete3_club", "children"),
     Output("athlete3_annivmax", "children"),
     Output('athl_card4', 'style'),
     Output("athlete4_nom", "children"),
     #Output("athlete4_achievements", "children"),
     Output("athlete4_club", "children"),
     Output("athlete4_annivmax", "children")],
    [Input('year-slider-athl', 'value'),
     Input('my_txt_input', 'value'),
     Input("display", "children")],
     prevent_initial_call=True)

def up_athletes(selected_year, txt_inserted, breakpoint_str):
    # Perform any manipulation on input_value and return the updated title
    print(txt_inserted)
    up_show = [{'display': 'none'}] * 4
    up_name = [''] * 4
    up_club = [''] * 4
    up_anniv = [''] * 4
    up_date_naiss = [''] * 4
    up_max = [''] * 4
    up_arr = [''] * 4
    up_epj = [''] * 4
    up_total = [''] * 4
    up_pdc = [''] * 4

    n = 0
    if txt_inserted is None:
        raise PreventUpdate
    for i in txt_inserted:
        up_name[n] = i
        df1 = df[(df['Nom'] == i) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
        df1 = df1.sort_values(by=['Date'], ascending=False)
        if len(df1['Club'].values[0]) > 21:
            up_club[n] = df1['Club'].values[0][0:20] + '.'
        else:
            up_club[n] = df1['Club'].values[0]
        up_show[n] = {'display': 'block'}
        up_anniv[n] = (df1['Né le'].values[0])[-4:]
        up_date_naiss[n] = (df1['Né le'].values[0])
        up_max[n] = str(df1['IWF'].max()) + ' IWF'
        up_arr[n] = str(df1['Arr'].max()) + '/'
        up_epj[n] = str(df1['EpJ'].max()) + '/'
        up_total[n] = df1['Total'].max()
        pdc_df = df1['Total'].idxmax()
        up_pdc[n] = str(df.loc[pdc_df, 'PdC']) + 'kg'
        n = n + 1
    if breakpoint_str == "xs" or breakpoint_str == "sm":
        return  up_show[0], f"{up_name[0]}", "" , "", \
                up_show[1], f"{up_name[1]}", "" , "", \
                up_show[2], f"{up_name[2]}", "" , "", \
                up_show[3], f"{up_name[3]}", "" , ""
    else:
        return  up_show[0], f"{up_name[0]}", f"{up_club[0]}", f"{up_anniv[0]}" + ' | PR ' + f"{up_max[0]}",  \
                up_show[1], f"{up_name[1]}", f"{up_club[1]}", f"{up_anniv[1]}" + ' | PR ' + f"{up_max[1]}",  \
                up_show[2], f"{up_name[2]}", f"{up_club[2]}", f"{up_anniv[2]}" + ' | PR ' + f"{up_max[2]}",  \
                up_show[3], f"{up_name[3]}", f"{up_club[3]}", f"{up_anniv[3]}" + ' | PR ' + f"{up_max[3]}"

# Gestion ouverture +Info Cartes Athlètes
@callback(
    [Output("athl-modal", "is_open"),
    Output("close-athl", "n_clicks")],
    [Input("open_athl1", "n_clicks"),
    Input("open_athl2", "n_clicks"),
    Input("open_athl3", "n_clicks"),
    Input("open_athl4", "n_clicks"),
    Input("close-athl", "n_clicks")],
    [State("athl-modal", "is_open")],
    prevent_initial_call=True
)


def toggle_modal_athl(open_clicks1, open_clicks2, open_clicks3, open_clicks4,  close_clicks, is_open_athl):
    if is_open_athl:
        is_open_athl = False
        open_clicks1 = None
        open_clicks2 = None
        open_clicks3 = None
        open_clicks4 = None
    if close_clicks:
        open_clicks1 = None
        open_clicks2 = None
        open_clicks3 = None
        open_clicks4 = None
        is_open_athl = False
        close_clicks = None
    if open_clicks1 or open_clicks2 or open_clicks3 or open_clicks4:
        is_open_athl = True
    print(str(open_clicks1) + ' ' + str(open_clicks2) + ' ' + str(open_clicks3) + ' ' + str(open_clicks4))
    return is_open_athl, close_clicks

@callback(
    [Output("athl-graph", "figure"),
     Output("athl-graph", "style"),
     Output("athl-table", "children"),
     Output("athl_sim-table", "children"),
     Output("athl_sim-table", "style"),
     Output("athlete_nom_info", "children"),
     Output('ach_aide-div_athl', 'style'),
     Output("athl_sim", "n_clicks")],
    [Input('my_txt_input', 'value'),
     Input("athl-modal", "is_open"),
     Input("athl_sim", "n_clicks"),
     Input("open_athl1", "n_clicks"),
     Input("open_athl2", "n_clicks"),
     Input("open_athl3", "n_clicks"),
     Input("open_athl4", "n_clicks")],
    prevent_initial_call=True
)

def update_table_athl4(txt_inserted, is_open_athl, is_open_athl_sim, open_clicks1, open_clicks2, open_clicks3, open_clicks4):
    if (not is_open_athl) or not txt_inserted:
        raise PreventUpdate
    athl = txt_inserted[0]
    if open_clicks2:
        athl = txt_inserted[1]
    if open_clicks3:
        athl = txt_inserted[2]
    if open_clicks4:
        athl = txt_inserted[3]

    df1 = df[(df['Nom'] == athl) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    df1 = df1.sort_values(by=['Date'], ascending=False)
    date_naiss = df1['Né le'].values[0]

    up_achievements = ''
    if df1['MondeSEN'].values[0] > 0:
        up_achievements = up_achievements + str(df1['MondeSEN'].values[0]) + ' x 🌎 | '
    if df1['MondeU20'].values[0] + df1['MondeU17'].values[0] > 0:
        up_achievements = up_achievements + str(
            df1['MondeU20'].values[0] + df1['MondeU17'].values[0]) + ' x 🌎🐥 | '
    if df1['MondeMasters'].values[0] > 0:
        if df1['Sexe'].values[0] == 'F':
            up_achievements = up_achievements + str(df1['MondeMasters'].values[0]) + ' x 🌎👵 | '
        else:
            up_achievements = up_achievements + str(df1['MondeMasters'].values[0]) + ' x 🌎👴 | '
    if df1['EuropeSEN'].values[0] > 0:
        up_achievements = up_achievements + str(df1['EuropeSEN'].values[0]) + ' x 🇪🇺 | '
    if df1['EuropeU23'].values[0] + df1['EuropeU20'].values[0] + df1['EuropeU17'].values[0] > 0:
        up_achievements = up_achievements + str(
            df1['EuropeU20'].values[0] + df1['EuropeU17'].values[0]) + ' x 🇪🇺🐥 | '
    if df1['FranceElite'].values[0] > 0:
        up_achievements = up_achievements + str(df1['FranceElite'].values[0]) + ' x 🇫🇷 | '
    if df1['GrandPrixFederal'].values[0] > 0:
        up_achievements = up_achievements + str(df1['GrandPrixFederal'].values[0]) + ' x 🐔 | '
    if df1['TropheeNationalU13'].values[0] > 0:
        up_achievements = up_achievements + str(df1['TropheeNationalU13'].values[0]) + ' x 🇫🇷👶 | '
    if df1['MondeMasters'].values[0] > 0:
        if df1['Sexe'].values[0] == 'F':
            up_achievements = up_achievements + str(df1['MondeMasters'].values[0]) + ' x 🌎👵 | '
        else:
            up_achievements = up_achievements + str(df1['MondeMasters'].values[0]) + ' x 🌎👴 | '
    if df1['EuropeMasters'].values[0] > 0:
        if df1['Sexe'].values[0] == 'F':
            up_achievements = up_achievements + str(df1['EuropeMasters'].values[0]) + ' x 🇪🇺👵 | '
        else:
            up_achievements = up_achievements + str(df1['EuropeMasters'].values[0]) + ' x 🇪🇺👴 | '
    if df1['NbCompet'].values[0] == 100:
        up_achievements = up_achievements + ' 💯 | '
    if df1['NbCompet'].values[0] == 50:
        up_achievements = up_achievements + ' 5️⃣0️⃣ | '
    if df1['Nb6sur6'].values[0] > 0:
        up_achievements = up_achievements + str(df1['Nb6sur6'].values[0]) + ' x 👌 | '
    if df1['Nb2sur6DerniereBarre'].values[0] > 0:
        up_achievements = up_achievements + str(df1['Nb2sur6DerniereBarre'].values[0]) + ' x 🫣 | '
    if df1['NbBulles'].values[0] > 0:
        up_achievements = up_achievements + str(df1['NbBulles'].values[0]) + ' x 🔴 | '
    if df1['NbDoublesBulles'].values[0] > 0:
        up_achievements = up_achievements + str(df1['NbDoublesBulles'].values[0]) + ' x 🔴🔴 | '
    if len(up_achievements) > 0:
        up_achievements = ' - ' + up_achievements
        up_show_ach_aide = {'display': 'block'}
    else:
        up_show_ach_aide = {'display': 'none'}
    athl_info_title = athl + ' ' + date_naiss + ' - ' + up_achievements


    dirname = os.path.dirname(__file__)
    path_db = os.path.join(dirname, 'dataltero.db')
    conn = sql.connect(database=path_db)
    qry = """SELECT cmp.SaisonAnnee as "Saison", clb.club, count(clb.club) as "Nb Compet",
                    max(cat.Arrache) as "Arr", max(cat.EpJete) as "EpJ", max(cat.PoidsTotal) as "Total"
                   , max(round(cat.IWF_Calcul,3)) as "IWF" 
                 FROM ATHLETE as ath 
                 LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                 LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                 LEFT JOIN CLUB as clb on clb.Club = cat.CATClub

                 where ath.Nom= :athlete
                 group by cmp.SaisonAnnee, clb.club
                 order by cmp.SaisonAnnee asc"""

    output_df = []
    hf_display = {'display': 'None'}
    if is_open_athl_sim:
        is_open_athl_sim = 0
        hf_display = {'display': 'block'}
        qry_hf = """SELECT * FROM (
                        SELECT
                            ROW_NUMBER() OVER (PARTITION BY rng.AtlNom ORDER BY rng.FinalScore DESC) as "Rang"		
                        ,   rng.Nom
                        ,   rng.Club
                        ,   rng.AnNaissance as "Naissance"
                        ,   round(rng.MaxIWF, 1) as "Max IWF"
                        ,   rng.MaxTotal as "Total"
                     
                         FROM (
                            SELECT
                                ath.nom
                            ,	cast(substr(ath."DateNaissanceFormat",1,4) as Integer)  as "AnNaissance"
                            ,	mxa.MaxIWF		        as "MaxIWF"
                            ,	mxa.MaxTotal		    as "MaxTotal"
                            ,   cla.Club
                            ,	cla.Latitude
                            ,   cla.Longitude
                            ,	atl.NOM			        as "AtlNom"
                            ,   atl.Club                as "AtlClub"
                            ,	atl.AnNaissance			as "AtlAnNaissance"
                            ,	atl.MaxIWF				as "AtlMaxIWF"
                            ,	atl.MaxTotal			as "AtlMaxTotal"
                            ,    cast(1.5 - NULLIF(
                                    ACOS(
                                        SIN(RADIANS(atl.latitude)) * SIN(RADIANS(cla.latitude)) +
                                        COS(RADIANS(atl.latitude)) * COS(RADIANS(cla.latitude)) * COS(RADIANS(atl.longitude - cla.longitude))
                                    ) * 6371, 
                                    0 
                                ) / 1000 as float)
                                * cast(case when atl.MaxIWF < mxa.MaxIWF
                                then
                                    atl.MaxIWF / mxa.MaxIWF
                                else
                                    mxa.MaxIWF / atl.MaxIWF
                                end as float)
                                * cast(case when atl.MaxTotal < mxa.MaxTotal
                                then
                                    cast(atl.MaxTotal as float) / cast(mxa.MaxTotal as float)
                                else
                                    cast(mxa.MaxTotal as float) / cast(atl.MaxTotal as float)
                                end as float)
                                * (0.7+POWER(1 - (ABS(cast(substr(ath."DateNaissanceFormat",1,4) as Float) - cast(atl.AnNaissance as Float)) / 80), 
                                    CASE WHEN cast(atl.AnNaissance as Float)>2011 THEN 6
                                         WHEN cast(atl.AnNaissance as Float)>2004 THEN 4
                                         WHEN cast(atl.AnNaissance as Float)>1990 THEN 2 ELSE 1 END)/(1/0.7))
                                    as "FinalScore"
                                                        
                            FROM ATHLETE as ath 
                            LEFT JOIN 
                                (select
                                    cat.AthleteID
                                 ,  cat.Sexe
                                 ,	max(cat.IWF_Calcul)		as "MaxIWF"
                                 ,	max(cat.PoidsTotal)		as "MaxTotal"
                                 from COMPET_ATHLETE as cat
                                 LEFT JOIN COMPET as cmp
                                    on cmp.NomCompetition = cat.CATNomCompetition
                                 LEFT JOIN 
                                    (	SELECT DISTINCT
                                            cmp.SaisonAnnee
                                        FROM COMPET cmp
                                        WHERE cmp.SaisonAnnee = 2024
                                        OR	  cmp.SaisonAnnee = 2025
                                    ) as cms
                                        on cms.SaisonAnnee = cmp.SaisonAnnee
                                 where cms.SaisonAnnee is not null
                                 group by cat.AthleteID
                                ) as mxa
                                on mxa.AthleteID = ath.AthleteID
                            LEFT JOIN 
                                (	SELECT
                                        ath.AthleteID
                                    ,   clb.Club
                                    ,	clb.Latitude   
                                    ,   clb.Longitude      
                                    ,   ROW_NUMBER() OVER (PARTITION BY ath.AthleteID ORDER BY cmp.DateCompet DESC) as row_num		
                                    FROM ATHLETE as ath 
                                    LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID = ath.AthleteID 
                                    LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                                    LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
                                    where cmp.SaisonAnnee in (2024, 2025)
                                ) as cla
                                on cla.AthleteID = ath.AthleteID
            
                            LEFT JOIN
                                (SELECT DISTINCT
                                    ath.Nom
                                ,   cla.Sexe
                                ,   ath.AthleteID
                                ,   cla.Club
                                ,	cast(substr(ath."DateNaissanceFormat",1,4) as Integer)	as "AnNaissance"
                                ,	mxa.MaxIWF
                                ,	mxa.MaxTotal
                                ,	cla.latitude
                                ,   cla.longitude
                                FROM ATHLETE as ath 
                                LEFT JOIN 
                                    (	SELECT
                                            ath.AthleteID
                                        ,   cat.Sexe
                                        ,   clb.Club
                                        ,	clb.Latitude   
                                        ,   clb.Longitude        
                                        ,   ROW_NUMBER() OVER (PARTITION BY ath.AthleteID ORDER BY cmp.DateCompet DESC) as row_num
                                        FROM ATHLETE as ath 
                                        LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                                        LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                                        LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
                                        where ath.Nom = :athlete
                                        
                                    ) as cla
                                    on cla.AthleteID = ath.AthleteID
                                
                                LEFT JOIN 
                                    (select
                                        cat.AthleteID
                                    ,	max(cat.IWF_Calcul)		as "MaxIWF"
                                    ,	max(cat.PoidsTotal)		as "MaxTotal"
                                    FROM COMPET_ATHLETE as cat
                                    LEFT JOIN COMPET as cmp
                                        on cmp.NomCompetition = cat.CATNomCompetition
                                    LEFT JOIN 
                                        (	SELECT DISTINCT
                                                cmp.SaisonAnnee
                                            FROM COMPET cmp
                                            where cmp.SaisonAnnee = 2024
                                            OR	  cmp.SaisonAnnee = 2025
                                        ) as cms
                                        on cms.SaisonAnnee = cmp.SaisonAnnee
                                     where cms.SaisonAnnee is not null
                                     group by cat.AthleteID
                                    ) as mxa
                                    on mxa.AthleteID = ath.AthleteID
                                        
                                where ath.Nom = :athlete
                                and cla.row_num = 1
                                )
                                as atl
                                    on 1=1
                            where cla.row_num = 1
                            and mxa.Sexe = atl.Sexe
                            and ath.nom <> atl.Nom
                            ) as rng
                        )
                    where rang<=10
                    """

        print("qry hf : " + str(time.time()))
        df_hf = pd.read_sql_query(qry_hf, conn, params=(athl, ))
        print(df_hf)
        output_df= [dbc.Table.from_dataframe(df_hf, responsive=True, striped=True, bordered=True, hover=True)]

        print("qry hf done : " + str(time.time()))
    #else:
    #    open_clicks1 = None
    #    open_clicks2 = None
    #    open_clicks3 = None
    #    open_clicks4 = None
        
    df_athl = pd.read_sql_query(qry, conn, params=(athl,))
    df_athl.head()

    print("qry r done : " + str(time.time()))
    df2_athl = df2[(df2['Nom'] == athl)]
    df2_athl['Série'] = pd.Categorical(df2_athl['Série'], ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "HON", "NAT", "INT B", "EUR", "INT A", "MON", "OLY"],
                                        ordered=True)
    df2_athl = df2_athl.sort_values(by=['Série'])
    print(df2_athl)
    fig_athl = px.histogram(df2_athl, x="Série", color="Catégorie",
                             color_discrete_sequence=["#DC4C64", "#3B71CA", "#E4A11B", "#14A44D", "#FBFBFB", "purple",
                                                      "#54B4D3", "#9FA6B2"],
                             category_orders={
                                 "Série": ["N.C.", "DEB", "DPT", "REG", "IRG", "FED", "HON", "NAT", "INT B", "EUR", "INT A", "MON", "OLY"]})

    fig_athl.update_layout(font_size=12,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.05,
                                xanchor="left",
                                x=-0.05
                            ))
    display_graph_athl = {'display': 'block'}

    return fig_athl, display_graph_athl, [dbc.Table.from_dataframe(df_athl, responsive=True, striped=True, bordered=True, hover=True)], \
       output_df, hf_display, athl_info_title, up_show_ach_aide, is_open_athl_sim

@callback(
    [Output("ag_datatable_athl", "columnDefs"),
     Output("ag_datatable_athl", "defaultColDef")],
    [Input("reset_col", "n_clicks"),
    Input("display", "children")],
)

def toggle_modal_athl(reset_clicks, breakpoint_str):
    color_mode = 'color'
    if breakpoint_str == "sm" or breakpoint_str == "xs":
        col_not_move = True
        print(breakpoint_str)
    else:
        col_not_move = False
    defaultColDef={"resizable": True, "sortable": True, "filter": True, "suppressMovable": col_not_move}

    if col_not_move == True:
        cols = [
            {
                "headerName": "Athlete",
                "children": [
                    {"field": "Nom", "width": 120, "pinned": "left", "hide": False},
                ],
            },
            {
                "headerName": "Arr.",
                "children": [
                    {"field": "Arr", "width": 60, "hide": False,
                     'cellStyle': {
                         "function": "params.value <=0 ? {" + color_mode + ": 'rgb(235, 61, 85)'} : {" + color_mode + ": 'rgb(59, 113, 202)'}",
                     },
                     },
                ],
            },
            {
                "headerName": "EpJ", "hide": False,
                "children": [
                    {"field": "EpJ", "width": 60, "hide": False,
                     'cellStyle': {
                         "function": "params.value <=0 ? {" + color_mode + ": 'rgb(235, 61, 85)'} : {" + color_mode + ": 'rgb(59, 113, 202)'}",
                     },
                     },
                ],
            },
            {
                "headerName": "Performance",
                "children": [
                    {"field": "Total", "width": 70, "hide": False, "font-weight": 'bold',
                     'cellStyle': {
                         "function": "params.value <=0 ? {" + color_mode + ": 'rgb(255, 41, 65)'} : {" + color_mode + ": 'rgb(44, 98, 217)'}",
                     },
                     },
                    {"field": "IWF", "width": 80, "hide": False, "valueFormatter": {"function": "params.value ? params.value.toFixed(3) : ''"}},
                    {"field": "Série", "width": 80, "hide": False},
                    {"field": "PdC", "width": 80, "hide": False, "valueFormatter": {"function": "params.value ? params.value.toFixed(2) : ''"}},
                    {"field": "Catégorie", "width": 100, "hide": False},
                ],
            },
            {
                "headerName": "Compétition",
                "children": [
                    {"field": "Date", "width": 100, "hide": False},
                    {"field": "Competition", "hide": False}
                ],
            }
        ]
    else:
        cols = [
                    {
                       "headerName": "Athlete",
                       "children": [
                            {"field": "Nom", "width": 200, "pinned": "left", "hide": False},
                        ],
                    },
                    {
                       "headerName": "Arraché",
                       "children": [
                            {"field": "Arr1", "headerName": "1", "width": 60, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                },
                            },
                            {"field": "Arr2", "headerName": "2", "width": 60, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                },
                            },
                            {"field": "Arr3", "headerName": "3", "width": 60, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                },
                            },
                            {"field": "Arr", "width": 75, "hide": False,
                                'cellStyle': {
                                    "function": "params.value <=0 ? {" + color_mode + ": 'rgb(235, 61, 85)'} : {" + color_mode + ": 'rgb(59, 113, 202)'}",
                                },
                            },
                        ],
                    },
                    {
                        "headerName": "Epaulé Jeté", "hide": False,
                            "children": [
                                {"field": "EpJ1", "headerName": "1", "width": 60, "hide": False,
                                    'cellStyle': {
                                        "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                    },
                                },
                                {"field": "EpJ2", "headerName": "2", "width": 60, "hide": False,
                                    'cellStyle': {
                                        "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                    },
                                },
                                {"field": "EpJ3", "headerName": "3", "width": 60, "hide": False,
                                    'cellStyle': {
                                        "function": "params.value <=0 ? {" + color_mode + ": 'rgb(220, 76, 100)'} : {" + color_mode + ": 'rgb(20, 164, 77)'}",
                                    },
                                },
                                {"field": "EpJ", "width": 75, "hide": False,
                                    'cellStyle': {
                                        "function": "params.value <=0 ? {" + color_mode + ": 'rgb(235, 61, 85)'} : {" + color_mode + ": 'rgb(59, 113, 202)'}",
                                    },
                                },
                            ],
                    },
                    {
                        "headerName": "Performance",
                            "children": [
                                {"field": "Total", "width": 70, "hide": False, "font-weight": 'bold',
                                 'cellStyle': {
                                     "function": "params.value <=0 ? {" + color_mode + ": 'rgb(255, 41, 65)'} : {" + color_mode + ": 'rgb(44, 98, 217)'}",
                                    },
                                 },
                                {"field": "IWF", "width": 80, "hide": False, "valueFormatter": {"function": "params.value ? params.value.toFixed(3) : ''"}},
                                {"field": "Série", "width": 80, "hide": False},
                                {"field": "PdC", "width": 80, "hide": False, "valueFormatter": {"function": "params.value ? params.value.toFixed(2) : ''"}},
                                {"field": "Catégorie", "width": 100, "hide": False},
                            ],
                    },
                    {
                        "headerName": "Compétition",
                        "children": [
                            {"field": "Date", "width": 150, "hide": False},
                            {"field": "Competition", "hide": False}
                            ],
                    }
            ]
    return cols, defaultColDef;

@callback(
    [Output("aide_achievements_athl", "is_open")],
    [Input("open-aide_achievements-athl", "n_clicks"),
    Input("close-aide_achievements-athl", "n_clicks")],
    [State("aide_achievements_athl", "is_open")],
    prevent_initial_call=True
)

# Aide Achievements
def toggle_modal_athl(open_clicks, close_clicks, is_open_athl):
    if open_clicks or close_clicks:
        is_open_athl = not is_open_athl
    return is_open_athl

@callback(
    [Output("ach_aide-table_athl", "children"),
    Output("ach_aide-txt_athl", "children")],
    [Input("aide_achievements_athl", "is_open")],
    prevent_initial_call=True
)

def update_table_athl1(is_open_ach):
    if not is_open_ach:
        raise PreventUpdate
    ach_aide_txt = 'Les symboles affichés à coté de la date de naissance de l''athlète représentent les participations ou performances détaillées dans le tableau ci-dessous : '
    ach = [['🌎', 'Championnats du Monde'], ['🇪🇺', 'Championnats d''Europe'], ['🇫🇷', 'France Elite'], ['🐥', 'Jeunes (U15 à U23)'], ['🇫🇷👶', 'Trophée National U13'], ['👵👴', 'Masters'],
           ['🐔', 'Grand Prix Fédéral'], ['💯', 'Au moins 100 Compétitions'], ['5️⃣0️⃣', 'Au moins 50 Compétitions'], ['👌', '6/6'],
           ['🫣', '2/6 sur les dernières barres des 2 mouvements'], ['🔴', 'Bulle'], ['🔴🔴', 'Double Bulle']]

    # Create the pandas DataFrame
    df_ach = pd.DataFrame(ach, columns=['Symbole', 'Signification'])
    if is_open_ach:
        return [dbc.Table.from_dataframe(df_ach, responsive=True, striped=True, bordered=True, hover=True)],
@callback(
    [Output("app_code_athl", "className"),
     Output("ag_datatable_athl", "className"),
     Output("reset_col", "color"),
     Output("excel_export", "color"),
     Output("bool_total", "label"),
     Output("year-slider-athl", "marks"),
     Output("zone_news", "className")],
    [Input("bool_light", "on")]
)

def light_mode_athl(on):
    if on == True:
        css_body = "body_light"
        css_grid = "ag-theme-quartz"
        reset_color = "secondary"
        reset_col_xl = "secondary"
        news_cn = "news_light"
        iwf_total_label = {"label": "IWF/Total", 'style': {"color": "rgb(40,40,45)"}}
        slider_marks = {str(year): {'label' : str(year), 'style':{'color':'rgb(40,40,45)'}} for year in df['SaisonAnnee'].unique()}
    else:
        css_body = "body"
        css_grid = "ag-theme-quartz-dark"
        reset_color = "light"
        reset_col_xl = "light"
        news_cn = "news"
        iwf_total_label = {"label": "IWF/Total", 'style': {"color": "white"}}
        slider_marks = {str(year): {'label' : str(year), 'style':{'color':'white'}} for year in df['SaisonAnnee'].unique()}

    print("d")
    return css_body, css_grid, reset_color, reset_col_xl, iwf_total_label, slider_marks, news_cn;

#Export Excel
clientside_callback(
    """async function (n, txt) {
        if (n) { 
            grid1Api = await dash_ag_grid.getApiAsync("ag_datatable_athl")
            var spreadsheets = [];
            if (typeof txt[0] === 'undefined') {
                s_name = 'Perfs_Athletes';
                f_name = 'perf_athletes.xlsx'
            } else if (txt.length === 1) {
                s_name = 'Perfs_' + txt[0];
                f_name = 'perf_' + txt[0] + '.xlsx'
            } else {
                s_name = 'Perfs_' + txt[0] + 'et+';
                f_name = 'perf_' + txt[0] + '_et_autres.xlsx'
            }
            spreadsheets.push(
                grid1Api.getSheetDataForExcel({ sheetName: s_name})
            );
            
            grid1Api.exportMultipleSheetsAsExcel({
              data: spreadsheets,
              fileName: f_name,
            });
        }
        return dash_clientside.no_update
    }""",
    Output("excel_export", "n_clicks"),
    Input("excel_export", "n_clicks"),
    State('my_txt_input', 'value'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    run_server(debug=True)

#@callback(
#    [Output("reset_col", "children"),
#     Output("excel_export", "children")],
#    [Input("display", "children")],
#     prevent_initial_call=False)

#def mobile_handling(breakpoint_str):
#    reset_txt="↪️"
#    excel_txt="💾"
#    if breakpoint_str not in ('xs', 'sm'):
#        reset_txt == "↪️ Reset"
#        excel_txt == "💾 Excel"
#    return reset_txt, excel_txt
