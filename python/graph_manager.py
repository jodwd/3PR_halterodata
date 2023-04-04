import dash
import plotly.express as px
from dash import dash_table
from dash import dcc
from dash import html
import pandas as pd
from dash.dependencies import Input, Output


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


df = pd.read_csv('C:/Users/joris/OneDrive/Documents/OldPC/Hobbies Productives - Copie/Haltero/haltero_data_full_2.csv',
                 sep=';')
df.head()
df = df.query("Nom in ['Elena AIGLE','Camille MOUNIER','Camille JOUNIAUX','Lisa LAMOTTE', 'Sara IAFRATE']")
df['Mois Compet'] = df['Mois Compet'].apply(str)
df['Mois Compet'] = pd.Categorical(df['Mois Compet'], ["8","9","10","11","12","1","2","3","4","5","6", "7"])
df = df.sort_values(by='Mois Compet')
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='my_txt_input',
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
            # selectionDirection='', # the direction in which selection occurred
            # selectionStart='',     # the offset into the element's text content of the first selected character
            # selectionEnd='',       # the offset into the element's text content of the last selected character
        )
    ]),

    # numpy.unique(df['DATA']))
    html.Datalist(id='Nom_athl', children=[
        html.Option(value="Lisa LAMOTTE"),
        html.Option(value="Elena AIGLE"),
        html.Option(value="Camille MOUNIER")
    ]),
    html.Br(),
    html.Br(),
    html.Div(id='div_output'),
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        df['SaisonAnnee'].min(),
        df['SaisonAnnee'].max(),
        step=None,
        value=df['SaisonAnnee'].max(),
        marks={str(year): str(year) for year in df['SaisonAnnee'].unique()},
        id='year-slider'
    ),
    html.Div([
        dash_table.DataTable(
            id='datatable-interactivity',
            # tab_selected_columns=['Nom', 'Date Naissance','Competition','Poids de Corps', 'Arrache','EpJete','Total','IWF'],
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True} for i in
                ['Nom', 'Date Naissance', 'Competition', 'Poids de Corps', 'Arrache', 'EpJete', 'TOTAL', 'IWF']
            ],
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=False,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
        ),
    ], className='data_tab'),
    html.Div(id='datatable-interactivity-container'),
    html.Link(
        rel='stylesheet',
        href='/assets/01_dash_board.css'
    )
])


@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])
@app.callback(
    Output('datatable-interactivity', "data"),
    [Input('year-slider', 'value'),
     Input(component_id='my_txt_input', component_property='value')
     ])
def update_figure(selected_year, txt_inserted):
    if txt_inserted:
        filtered_df = df[(df['Nom'] == txt_inserted) & (df['SaisonAnnee'] == selected_year)]
    else:
        filtered_df = df[df['SaisonAnnee'] == selected_year]

    fig = px.scatter(filtered_df, x="Mois Compet", y="IWF_Points",
                     hover_name="Competition", color="Nom",
                     log_x=False, size_max=55)

    fig.update_layout(transition_duration=5)
    return fig


def update_data(selected_year, txt_inserted):
    if txt_inserted:
        filtered_df = df[(df['Nom'] == txt_inserted) & (df['SaisonAnnee'] == selected_year)]
    else:
        filtered_df = df[df['SaisonAnnee'] == selected_year]

    dat = filtered_df.to_dict('records')

    return dat


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
