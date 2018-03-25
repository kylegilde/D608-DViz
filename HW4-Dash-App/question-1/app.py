# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import numpy as np
from scipy.stats.mstats import gmean
import datetime as dt

###Part 1: DATA MUNGING
# load data
rk_data = pd.read_csv(
    "https://raw.githubusercontent.com/charleyferrari/CUNY_DATA_608/master/module4/Data/riverkeeper_data_2013.csv")

# clean & transform data
rk_data.Date = pd.to_datetime(rk_data.Date)

rk_data.EnteroCount = rk_data.EnteroCount.str.extract('(\d+)').astype("int64")

rk_data['WeekofMonth'], rk_data['Month'], rk_data['Year'] = pd.Categorical(
    np.ceil(rk_data.Date.dt.day / 7).astype("int64"), ordered=True), \
                                                            pd.Categorical(rk_data.Date.dt.month, ordered=True), \
                                                            rk_data.Date.dt.year

rk_data.WeekofMonth[rk_data.WeekofMonth == 5] = 4
rk_data['EnteroCountsGreaterThan110'] = rk_data.EnteroCount > 110
rk_data["MinYear"], rk_data["MaxYear"], rk_data["GMeanEnteroCount"], rk_data[
    "MeanRainAmount"] = rk_data.Year, rk_data.Year, rk_data.EnteroCount, rk_data.FourDayRainTotal

df_rk = pd.pivot_table(rk_data,
                       index=["Month", "WeekofMonth", "Site"],
                       aggfunc={
                           'GMeanEnteroCount': gmean,
                           'SampleCount': "count",
                           'EnteroCountsGreaterThan110': np.sum,
                           'MeanRainAmount': np.mean,
                           'MinYear': np.min,
                           'MaxYear': np.max
                       }).reset_index()

# https://stackoverflow.com/questions/20119414/define-aggfunc-for-each-values-column-in-pandas-pivot-table?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# https://stackoverflow.com/questions/36377501/create-complicated-conditional-column-geometric-mean-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

# Create safety indicator
NotSafe1 = df_rk.EnteroCountsGreaterThan110 > 0
NotSafe2 = (df_rk.SampleCount >= 5) & (df_rk.GMeanEnteroCount > 30)
df_rk["HistoricallySafe"] = np.invert(NotSafe1 | NotSafe2)

# Sort by the best site per week of the month
df_rk["BestSite"] = df_rk.sort_values(['HistoricallySafe', 'EnteroCountsGreaterThan110', 'MeanRainAmount'],
                                      ascending=[False, True, False]) \
                        .groupby(["Month", "WeekofMonth"]) \
                        .cumcount() + 1

# df_rk[["Month", "WeekofMonth", "BestSite",'HistoricallySafe','EnteroCountsGreaterThan110', 'MeanRainAmount']]\
#     .sort_values(["Month", "WeekofMonth", "BestSite"]).tail(10)
# df_rk.to_csv("mydf.csv")

df_rk.describe()
df_rk.info()
df_rk.tail(10)
np.sum(df_rk.HistoricallySafe) / df_rk.HistoricallySafe.count()

def generate_table(dataframe, max_rows=10):
    """
    Generate an HTML table
    """
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

###Part 2: CREATE WEB APP
app = dash.Dash()
month_dropdown_items = df_rk.Month.unique()
week_dropdown_items = df_rk.WeekofMonth.unique()

colors = {
    'background': '#000099',
    'text': '#ffffff'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Welcome to your Hudson River Kayaking Site Guide',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.H2(
        children='CUNY DATA608 Data Viz',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H2(
        children='by Kyle Gilde',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H3(
        children='Pick a month & week below to see the best and safest sites',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    # html.Div(children=
    #     [
            #html.Label('Month'),
    dcc.Dropdown(
        id="select-month",
        options=[
            {'label': i, 'value': i} for i in month_dropdown_items
        ],
        searchable=False,
        placeholder="Select a month number"
    ),

    #https://community.plot.ly/t/how-to-populate-a-dropdown-from-unique-values-in-a-pandas-data-frame/5543/2
    #html.Label('Week'),
    dcc.Dropdown(
        id="select-week",
        options=[
            {'label': i, 'value': i} for i in week_dropdown_items
        ],
        searchable=False,
        placeholder="Select a week of the month"
    ),
    #style={'width': '50%'}
    # , 'display': 'inline-block'
    # style={'columnCount': 2}
    # ),
    #],

    # html.Div(children='The safest and best site.', style={
    #     'textAlign': 'center',
    #     'color': colors['text']
    # }),

    dcc.Graph(
        id='example-graph-2',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
])

if __name__ == '__main__':
   app.run_server(debug=False)