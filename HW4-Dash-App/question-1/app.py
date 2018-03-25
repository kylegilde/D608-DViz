# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
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
rk_data["MonthWeek"] = 'Month ' + rk_data.Month.astype('str').str.cat(rk_data.WeekofMonth.astype('str'), sep=' - Week ')

#Pivot Calculations
df_rk = pd.pivot_table(rk_data,
                       index=["MonthWeek", "Site"],
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
df_rk["HistoricallySafe"] = np.invert(NotSafe1 | NotSafe2).astype('str')

# Sort by the best site per week of the month
df_rk["BestSite"] = df_rk.sort_values(['HistoricallySafe', 'EnteroCountsGreaterThan110', 'MeanRainAmount'],
                                      ascending=[False, True, False]) \
                        .groupby(["MonthWeek"]) \
                        .cumcount() + 1

# Round decimals
df_rk.MeanRainAmount, df_rk.GMeanEnteroCount = df_rk.MeanRainAmount.round(2), df_rk.GMeanEnteroCount.round(0)
# Re-order columns
df_rk = df_rk[['MonthWeek', 'BestSite', 'Site', 'HistoricallySafe', 'MeanRainAmount',
               'SampleCount', 'EnteroCountsGreaterThan110', 'GMeanEnteroCount', 'MinYear', 'MaxYear']]

def generate_table(dataframe, max_rows=20):
    """Creates HTML Table"""
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
dropdown_items = df_rk.MonthWeek.unique()

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
        children='Pick a month & week below to see the best site for that time of year',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.H4(
        children='If available, the best site will be one that has been "historically safe" (without any Entero Count issues) and with the highest rainfall average',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    dcc.Dropdown(
        id="select-month-week",
        options=[
            {'label': i, 'value': i} for i in dropdown_items
        ],
        searchable=False,
        placeholder="Select a Month & Week"
    ),
    html.Div(id='my-table', style={'color': colors['text']})
 ])

# https://community.plot.ly/t/how-to-populate-a-dropdown-from-unique-values-in-a-pandas-data-frame/5543/2
# https://community.plot.ly/t/display-tables-in-dash/4707

@app.callback(Output('my-table', 'children'),[Input('select-month-week', 'value')])
def table_update(value):
    df1 = df_rk[df_rk.MonthWeek == value].sort_values(["BestSite"])
    df1 = df1.drop("MonthWeek", axis=1)
    return generate_table(df1)

if __name__ == '__main__':
   app.run_server(debug=True)
