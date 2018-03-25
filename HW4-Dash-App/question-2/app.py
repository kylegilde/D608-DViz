import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd


import datetime as dt


###Part 1: DATA MUNGING
# load data
df = pd.read_csv(
    "https://raw.githubusercontent.com/charleyferrari/CUNY_DATA_608/master/module4/Data/riverkeeper_data_2013.csv")

# clean & transform data
df.EnteroCount = df.EnteroCount.str.extract('(\d+)').astype("int64")
df['Year'] = pd.Categorical(pd.to_datetime(df.Date).dt.year.astype("int64"), ordered=True)

###Part 2: CREATE WEB APP

app = dash.Dash()
dropdown_items = df.Site.unique()
years = df.Year.unique()

app.layout = html.Div([
    html.H1(
        children='The Effects of Rainfall on Water Quality in the Hudson River',
        style={'textAlign': 'center'}
    ),
    html.H2(
        children='CUNY DATA608 Data Viz',
        style={'textAlign': 'center'}
    ),

    html.H2(
        children='by Kyle Gilde',
        style={'textAlign': 'center'}
    ),

    html.H3(
        children='Select a Hudson River Site in order to see the relationship between the 4-day rainfall total and amount of Enterococcus in the sample.',
        style={'textAlign': 'center'}
    ),

    html.H3(
        children='The years can be filtered by clicking on the colors in the Legend.',
        style={'textAlign': 'center'}
    ),

    dcc.Dropdown(
        id="select-site",
        options=[
            {'label': i, 'value': i} for i in dropdown_items
        ],
        searchable=False,
        placeholder="Select a Hudson Site"
    ),
    dcc.Graph(id='my-graph')
])

@app.callback(Output('my-graph', 'figure'),[Input('select-site', 'value')])
def graph_update(site_value):
    new_df = df[df['Site'] == site_value]
    return {
        'data': [
            go.Scatter(
                x=new_df[new_df['Year'] == i]['FourDayRainTotal'],
                y=new_df[new_df['Year'] == i]['EnteroCount'],
                mode='markers',
                opacity=0.8,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ) for i in years
        ],
        'layout': go.Layout(
            xaxis={'type': 'log', 'title': 'FourDayRainTotal (log scale)'},
            yaxis={'type': 'log', 'title': 'EnteroCount (log scale)'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)

#https://dash.plot.ly/getting-started-part-2
#https://dash.plot.ly/getting-started#dash-app-layout
