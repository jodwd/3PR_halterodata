# In this example, the app layout is defined using the dash_html_components and dash_core_components modules.
# The layout includes two graphs, a dropdown menu, and radio buttons.
# The first graph (graph1) displays a bar chart, line chart, or scatter chart depending on the selected radio button.
# The second graph (graph2) displays a pie chart showing the distribution of a selected variable for a selected category.
# The callback functions update the graphs based on user input. The first callback updates graph1 based on the selected dropdown variable and radio button chart type.
# The second callback updates graph2 based on the clicked point on graph1.

#Overall, this dashboard demonstrates the use of various Plotly charts, interactive controls, and callback functions to create a complex and dynamic dashboard.

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Load data
df = pd.read_csv('data.csv')

# Define app layout
app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H1('My Dashboard', style={'textAlign': 'center'}),
        dcc.Graph(id='graph1', figure={})
    ], className='twelve columns'),
    html.Div([
        html.Div([
            html.Label('Select a variable to plot'),
            dcc.Dropdown(
                id='dropdown1',
                options=[{'label': col, 'value': col} for col in df.columns],
                value='variable1'
            )
        ], className='six columns'),
        html.Div([
            html.Label('Select a chart type'),
            dcc.RadioItems(
                id='radio1',
                options=[{'label': 'Bar Chart', 'value': 'bar'},
                         {'label': 'Line Chart', 'value': 'line'},
                         {'label': 'Scatter Chart', 'value': 'scatter'}],
                value='bar'
            )
        ], className='six columns')
    ], className='twelve columns'),
    html.Div([
        dcc.Graph(id='graph2', figure={})
    ], className='twelve columns')
])

# Define callback for graph1
@app.callback(Output('graph1', 'figure'),
              [Input('dropdown1', 'value'),
               Input('radio1', 'value')])
def update_graph1(variable, chart_type):
    if chart_type == 'bar':
        fig = px.bar(df, x='category', y=variable, color='category')
    elif chart_type == 'line':
        fig = px.line(df, x='date', y=variable, color='category')
    else:
        fig = px.scatter(df, x='date', y=variable, color='category')
    fig.update_layout(title=variable + ' by Category', xaxis_title='Category', yaxis_title=variable)
    return fig

# Define callback for graph2
@app.callback(Output('graph2', 'figure'),
              [Input('graph1', 'clickData')])
def update_graph2(clickData):
    if clickData:
        category = clickData['points'][0]['x']
        df_filtered = df[df['category'] == category]
        fig = px.pie(df_filtered, names='variable1', values='value1')
        fig.update_layout(title='Distribution of variable1 for ' + category)
    else:
        fig = {}
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)