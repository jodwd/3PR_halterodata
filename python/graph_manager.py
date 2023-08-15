import dash
import plotly.express as px
from dash import dash_table
from dash import dcc
from dash import html
from dash.exceptions import PreventUpdate
import pandas as pd
import sqlite3 as sql
import numpy as np
from dash.dependencies import Input, Output
from flask import Flask, render_template


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
conn = sql.connect(database="dataltero.db")
cur = conn.cursor()
qry = "SELECT * from haltero_data_full"
qry = "SELECT * from COMPET_ATHLETE"
qry = "SELECT * from COMPET"
qry = "SELECT * from ATHLETE"
qry = "SELECT * FROM ATHLETE as ath " \
      "LEFT JOIN COMPET_ATHLETE as cat on cat.CATLicence = ath.Licence " \
      "LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition " \
      "LEFT JOIN CLUB as clb on clb.Club = cat.CATClub"
#df = pd.read_csv('C:/Users/joris/PycharmProjects/halterodata/output/haltero_data_full.csv', sep=';')
df = pd.read_sql_query(qry, conn)
df.head()
df = df
df['MoisCompet'] = pd.Categorical(df['MoisCompet'], ["08","09","10","11","12","01","02","03","04","05","06","07"])
df = df.sort_values(by='MoisCompet')

#df.head()
#df = df
#df['MoisCompet'] = df['MoisCompet'].apply(str)
#df['MoisCompet'] = pd.Categorical(df['MoisCompet'], ["8","9","10","11","12","1","2","3","4","5","6", "7"])
#df = df.sort_values(by='MoisCompet')
updated_title='Haltero Data'
app = dash.Dash(__name__)

#df_unique_names = df['Nom'].unique  # Fetch or generate data from Python
list_names = list(set(df['Nom'].tolist()))

#body
app.layout = html.Div([
    #Header & filtres
    html.Div([
        # Titre
        html.Div(
            children=[
                html.P("Haltero Data")
            ],
            id='filter_info',
            className="text-box",
        ),
        # Zone filtres athlètes
        html.Div([
            html.Div([
                # Selection Athlète #1
                html.Div(
                    children=[
                        html.P("Athlète #1")
                    ],
                    id='athl1_info',
                    className="athl1_box",
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
                    className="input_box1",
                )] ,
                className="athl1_zone",
            ),
            html.Datalist(id='Nom_athl'),

            #Selection Athlète #2
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
                        inputMode='latin',  # provides a hint to browser on type of data that might be entered by the user.
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
            value=[df['SaisonAnnee'].max()-1,df['SaisonAnnee'].max()],
            marks={str(year): str(year) for year in df['SaisonAnnee'].unique()},
            id='year-slider',
            className = 'slider_zone')],
        id='div_output',
        className='graph_box'
    ),
    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            # tab_selected_columns=['Nom', 'DateNaissance','NomCompetition','Poids de Corps', 'Arrache','EpJete','Total','IWF'],
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in
                    ['Nom', 'DateNaissance', 'NomCompetition', 'Poids de Corps', 'Arr1', 'Arr2', 'Arr3', 'EpJ1','EpJ2','EpJ3', 'PoidsTotal', 'IWF_Calcul']
            ],
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold'
            },
            style_data={
                'backgroundColor': 'rgb(80, 80, 90)',
                'color': 'white'
            },
            row_selectable="multi",
            row_deletable=False,
            selected_columns=[],
            selected_rows=[],
            style_as_list_view=True,
            page_action="native",
            page_current=0,
            page_size=10,
        ),
    ], className='data_tab'),
    html.Div(id='datatable-interactivity-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/01_dash_board.css'
        ),
    html.Div(id='none',children=[],style={'display': 'none'})
    ],
    id='app_code',
    className='body'
)


#@app.callback(
#    Output('Nom_athl', 'children'),
#    [Input('my_txt_input', 'value')]
#)
#def update_datalist(input_value):
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


@app.callback(
    Output('Nom_athl', 'children'),
    [Input('none', 'children')]
)
def update_datalist(none):
    children = []  # List to store dynamic options

    children = [html.Option(value=val, children=val) for val in list_names]

    return children
@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)

def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


#@app.callback(
#    Output('datatable-interactivity-container', "children"),
#    Input('datatable-interactivity', "derived_virtual_data"),
#    Input('datatable-interactivity', "derived_virtual_selected_rows"))


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_figure(selected_year, txt_inserted, txt_inserted2):
    if selected_year=='':
        selected_year=df['SaisonAnnee'].max()
    if (txt_inserted!='' and txt_inserted2!=''):
        filtered_df = df[((df['Nom'] == txt_inserted) | (df['Nom'] == txt_inserted2)) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    elif (txt_inserted=='' and txt_inserted2 !=''):
        filtered_df = df[(df['Nom'] == txt_inserted2) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    elif (txt_inserted!='' and txt_inserted2==''):
        filtered_df = df[(df['Nom'] == txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    else:
        filtered_df = df[(df['Nom'] == 'Camille MOUNIER') & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

    fig = px.scatter(filtered_df, x="AnneeMois", y="IWF_Calcul",
                     hover_name="NomCompetition", color="Nom",
                     log_x=False, size_max=55)
    fig.update_traces(marker = dict(
                            size=10,
                            symbol='circle'))

    fig.update_xaxes(categoryorder="category ascending")
    fig.update_layout(transition_duration=5,
                      plot_bgcolor='rgb(40,40,45)',
                      paper_bgcolor='rgb(40,40,45)',
                      font_color="white",
                      title_font_color="white",
                      legend_title_font_color="white")
    return fig


@app.callback(
    [Output('datatable-interactivity', "data"),
     Output('datatable-interactivity', "columns")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_data(selected_year=None, txt_inserted=None, txt_inserted2=None):
    if selected_year=='':
        selected_year=df['SaisonAnnee'].max()
    if txt_inserted!='':
        filtered_df = df[((df['Nom'] == txt_inserted) | (df['Nom'] == txt_inserted2)) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
    else:
        filtered_df = df[(df['Nom'] == 'Camille MOUNIER') & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]

    columns = [
            {"name": i, "id": i, "deletable": True, "selectable": True} for i in
            ['Nom', 'DateNaissance', 'NomCompetition', 'Poids de Corps', 'Arr1', 'Arr2', 'Arr3', 'EpJ1','EpJ2','EpJ3', 'PoidsTotal', 'IWF_Calcul']
    ]

    dat = filtered_df.to_dict('records')

    return dat, columns
@app.callback(
    Output("filter_info", "children"),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def update_title(selected_year, txt_inserted, txt_inserted2):
    # Perform any manipulation on input_value and return the updated title
    global updated_title
    if min(selected_year)==max(selected_year):
        year_text = 'Saison ' + str(max(selected_year))
    else:
        year_text = 'Saisons ' + str(min(selected_year)) + '/' + str(max(selected_year))

    if (txt_inserted=='' and txt_inserted2==''):
        raise PreventUpdate
    if (txt_inserted!='' and txt_inserted2==''):
        updated_title = f"{txt_inserted}\n{year_text}"
    if ((txt_inserted=='') and txt_inserted2!=''):
        updated_title = f"{txt_inserted2}\n{year_text}"
    if (txt_inserted!='' and txt_inserted2!=''):
        updated_title = f"{txt_inserted} vs {txt_inserted2}\n{year_text}"

    return updated_title

@app.callback(
    [Output("athlete1_nom", "children"),
     Output("athlete1_club", "children"),
     Output("athlete1_anniv", "children"),
     Output("athlete1_max", "children"),
     Output("athlete1_total", "children"),
     Output("athlete1_pdc", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])

def updated_name(selected_year, txt_inserted):
    # Perform any manipulation on input_value and return the updated title
    if txt_inserted=='' or selected_year=='':
        raise PreventUpdate
    else:
        updated_name = txt_inserted
        df1 = df[(df['Nom'] == txt_inserted) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
        if len(df1['Club'].values[0]) > 21:
            updated_club = df1['Club'].values[0][0:20] + '.'
        else:
            updated_club = df1['Club'].values[0]
        updated_anniv = df1['DateNaissance'].values[0]
        updated_max = round(df1['IWF_Calcul'].max(),3)
        updated_arr = df1['Arrache'].max()
        updated_epj = df1['EpJete'].max()
        updated_total = df1['PoidsTotal'].max()
        pdc_df = df1['PoidsTotal'].idxmax()
        updated_pdc=df.loc[pdc_df, 'Poids de Corps']

        return f"{updated_name}", f"{updated_club}", f"{updated_anniv}", f"{updated_max} IWF", f"{updated_arr}/{updated_epj}/{updated_total}", f"{updated_pdc} PdC"

@app.callback(
    [Output("athlete2_nom", "children"),
     Output("athlete2_club", "children"),
     Output("athlete2_anniv", "children"),
     Output("athlete2_max", "children"),
     Output("athlete2_total", "children"),
     Output("athlete2_pdc", "children")],
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input2', component_property='value')
     ])

def updated_name(selected_year, txt_inserted2):
    # Perform any manipulation on input_value and return the updated title
    if txt_inserted2=='' or selected_year=='':
        raise PreventUpdate
    else:
        updated_name2 = txt_inserted2
        df2 = df[(df['Nom'] == txt_inserted2) & (df['SaisonAnnee'] >= min(selected_year)) & (df['SaisonAnnee'] <= max(selected_year))]
        if len(df2['Club'].values[0]) > 21:
            updated_club2 = df2['Club'].values[0][0:20] + '.'
        else:
            updated_club2 = df2['Club'].values[0]
        updated_anniv2 = df2['DateNaissance'].values[0]
        updated_max2 = round(df2['IWF_Calcul'].max(),3)
        updated_arr2 = df2['Arrache'].max()
        updated_epj2 = df2['EpJete'].max()
        updated_total2 = df2['PoidsTotal'].max()
        pdc_df2 = df2['PoidsTotal'].idxmax()
        updated_pdc2=df.loc[pdc_df2, 'Poids de Corps']

        return f"{updated_name2}", f"{updated_club2}", f"{updated_anniv2}", f"{updated_max2} IWF", f"{updated_arr2}/{updated_epj2}/{updated_total2}", f"{updated_pdc2} PdC"


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
