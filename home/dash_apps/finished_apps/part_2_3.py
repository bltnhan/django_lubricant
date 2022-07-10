import dash
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.dash_table import DataTable, FormatTemplate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
from . import lib, table_bars
from dash import dash_table as dt
import dash_bootstrap_components as dbc
import pathlib
import urllib.request
import numpy as np
import plotly.express as px
import urllib.request
import requests
import datetime
import os
import sys
from queue import Queue
import threading
import time

progress_queue = Queue(1)
progress_memeory = 0

# DJANGO_VERSION
file_name = str(pathlib.Path(__file__).name)[:-3]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets, add_bootstrap_links=True)
app.css.append_css({"external_url": "/static/css/s1.css"})


#get time update
data_path = 'home/dash_apps/finished_apps/data/data.xlsx'
oil_path = 'home/dash_apps/finished_apps/data/oil_application.xlsx'
m_time = os.path.getmtime(data_path)
date_time = datetime.datetime.fromtimestamp(m_time)
d = date_time.strftime("%m/%d/%Y, %H:%M:%S")

# call df
df = pd.read_excel(data_path, sheet_name=0, usecols='A:AJ')
df_oil = pd.read_excel(oil_path, sheet_name=0, usecols='A:E')
mapping = {df.columns[0]: 'ID', df.columns[1]: 'MONTH', df.columns[2]: 'YEAR', df.columns[3]: 'TAX_CODE',
           df.columns[4]: 'IMPORTER_NAME', df.columns[5]: 'INDUSTRY',
           df.columns[6]: 'INDUSTRY_CODE', df.columns[7]: 'CLASS', df.columns[8]: 'CLASS_CODE',
           df.columns[9]: 'COMPANY_CLASSIFICATION', df.columns[10]: 'COMPANY_CLASSIFICATION_CODE',
           df.columns[11]: 'CITY', df.columns[12]: 'HSCODE', df.columns[13]: 'DESCRIPTION_VN',
           df.columns[14]: 'TYPE_OF_OIL', df.columns[15]: 'TYPE_CODE', df.columns[16]: 'BASE_OIL_FINISH_GOOD',
           df.columns[17]: 'OIL_CLASS_CODE', df.columns[18]: 'MOTHER_BRAND', df.columns[19]: 'MOTHER_BRAND_CODE',
           df.columns[20]: 'MAIN_BRAND', df.columns[21]: 'MAIN_BRAND_CODE', df.columns[22]: 'OIL_APPLICATION_CODE',
           df.columns[23]: 'OIL_APPLICATION_CHECK', df.columns[24]: 'VICOSITY_SPEC', df.columns[25]: 'QTY',
           df.columns[26]: 'UOM', df.columns[27]: 'PACK_SIZE', df.columns[28]: 'PACK_SPEC',
           df.columns[29]: 'QUANTITY_PER_PACK', df.columns[30]: 'VOLUME', df.columns[31]: 'SEGMENT',
           df.columns[32]: 'TOTAL_INV_VALUE',
           df.columns[33]: 'CURRENCY', df.columns[34]: 'EXCHANGE_TO_USD', df.columns[35]: 'TOTAL_AMT'
           }
df.rename(columns=mapping, inplace=True)

df['CLASS'] = df['CLASS_CODE'].apply(lambda x: "Client" if x == 3 else "Trading" if x == 2 else "Competitor")
df = df[['MONTH', 'YEAR', 'CLASS', 'SEGMENT', 'MOTHER_BRAND', 'VOLUME', 'TOTAL_AMT', 'INDUSTRY']]
# covert type du lieu
df = df[(df['VOLUME'] != "UNSPECIFY") & (df['TOTAL_AMT'] != "UNSPECIFY")]
df['VOLUME'] = pd.to_numeric(df['VOLUME'], downcast="float")
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], downcast="float")
df['SEGMENT'] = df['SEGMENT'].replace('b2b', 'B2B')
df['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
df['TOTAL_AMT'] = df['TOTAL_AMT'].map('{:,.2f}'.format)
# df = df[df['CLASS']=='Competitor']

# TAO LIST MONTH, YEAR
lst_month_org = list(df['MONTH'].unique())
lst_month = []
month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_list = month_list[::-1]
# append list column not in
for mon in month_list:
    if mon in lst_month_org:
        lst_month.append(mon)

lst_year = list(df['YEAR'].unique())

# df = df[(df['MOTHER_BRAND']!=0) & (df['MOTHER_BRAND'].str.contains('unbrand'))]
df_groupby = df.groupby(by=['MONTH', 'YEAR', 'CLASS', 'SEGMENT', 'MOTHER_BRAND', 'INDUSTRY']).agg(
    {'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()
df_groupby['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df_groupby['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')

# title
title_page = 'Part 2C: Competitor Import by Volume in'

app.layout = dbc.Container([
    # ----------------------------------------------------------------
    # Title, header
    dbc.Row([
        html.Meta(httpEquiv="refresh", content="60")
    ]),
    dbc.Row([
        dbc.Col(
            html.H6(f'Last update on: {d}',
                    id='my_h6',
                    style={'text-align': 'left', 'font-decoration': 'italic', 'font-family': 'Arial'}
                    ))
    ]),

    dbc.Row([
        dbc.Col(
            html.H1(children=
                    title_page,
                    id='my_h1',
                    className='text-center text-success, mb-4'),
            style={'font-family': 'Arial'},
            width=12)
    ]),
    # ----------------------------------------------------------------
    # Filter
    dbc.Row([
        dbc.Col([
            html.P('Select below options filters:',
                   style={'font-size': 13, 'font-family': 'Arial', 'color': '#007DBF', 'text-align': 'left'}),
            dcc.Dropdown(
                id='my_dd_year',
                multi=True,
                disabled=False,
                style={'display': True},
                placeholder='SELECT YEAR',
                value='2022',
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['YEAR'].unique()) + ['Select All']],
                className='text-primary'
            ),
            html.Br(),
            dcc.Dropdown(
                id='my_dd_month',
                multi=True,
                disabled=False,
                style={'display': True},
                placeholder='SELECT MONTH',
                value=['JAN'],
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['MONTH'].unique()) + ['Select All']],
                className='text-primary'
            ),
            html.Br(),
            dcc.Dropdown(
                id='my_dd_class',
                multi=True,
                disabled=False,
                style={'display': True},
                placeholder='SELECT CLASS',
                value=['Competitor'],
                clearable=True,
                options=['Competitor'],
                className='text-primary',
            ),
            html.Br(),
            dcc.Dropdown(
                id='my_dd_segment', multi=True, value=['B2B'],
                clearable=True,
                placeholder='SELECT SEGMENT',
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['SEGMENT'].unique()) + ['Select All']],
                className='text-primary'
            ),
            html.Br(),
            # ----------------------------------------------------------------
            # Download button
            dbc.Col([
                html.Div(children=[
                    html.H4(children='Update Latest Data', className="text text-info",
                            style={'font-family': 'Arial', 'font-size': '16px'}, ),
                    dcc.Interval(id='clock', interval=1000, n_intervals=0, max_intervals=-1),
                    dbc.Progress(value=0, id="progress_bar"),
                    dash.html.Button("Click for Update", id='start_work', n_clicks=0, className="btn btn-danger",
                                     style={'font-family': 'Arial'}, )
                ],
                ),
            ]),
        ], className='g-2 align-self-start', style={"padding": "5px", "margin": "5px"}, width={"size": 2}
        ),

        dbc.Col([
            dt.DataTable(
                id='my_datatable_1',
                page_size=10,
                sort_action="native",
                style_table={"overflowX": "auto"},
                sort_mode="multi",
                # virtualization=True,
                style_cell={'textAlign': 'left',
                            'min-width': '100px',
                            'backgroundColor': '#F2F2F2',
                            'font-family': 'Arial',
                            },
                style_as_list_view=False,
                style_header={
                    'backgroundColor': '#007DBF',
                    'fontWeight': 'bold',
                    'font': 'Arial',
                    'color': 'white',
                    'border': '1px solid #638E9E'
                },
                style_data_conditional=(
                    [
                        {
                            'if': {
                                'column_type': 'text'
                            },
                            'textAlign': 'left'
                        },
                        # Format active cells *********************************
                        {
                            'if': {
                                'state': 'active'  # 'active' | 'selected'
                            },
                            'border': '3px solid rgb(0, 116, 217)'
                        },
                        {
                            'if': {
                                'column_editable': False  # True | False
                            },
                            'cursor': 'not-allowed'
                        },
                    ]
                    # +
                    # data_bars(df_groupby, 'VOLUME')
                ),
                style_data={'textOverflow': 'hidden', 'color': 'black',
                            'border': '1px solid orange', 'height': 'auto'},
            ),
        ]),
        dbc.Col([
            dcc.Graph(
                id="piechart_1",
            ),
            dcc.Graph(
                id="piechart_2",
            ),
        ])
    ], align='top', justify='center', className='g-2'),

], fluid=True)


# ----------------------------------------------------------------
# Callbacks day/month/class/segment
@app.callback(
    Output('my_dd_year', 'value'),
    Input('my_dd_year', 'options'))
def get_year_value(my_dd_year):
    return [k['value'] for k in my_dd_year]


@app.callback(
    Output('my_dd_month', 'value'),
    Input('my_dd_month', 'options'))
def get_month_value(my_dd_month):
    return [k['value'] for k in my_dd_month]


# @app.callback(
#     Output('my_dd_class', 'value'),
#     Input('my_dd_class', 'options'))
# def get_class_value(my_dd_class):
#     return [k['value'] for k in my_dd_class]

@app.callback(
    Output('my_dd_segment', 'value'),
    Input('my_dd_segment', 'options'))
def get_segment_value(my_dd_segment):
    return [k['value'] for k in my_dd_segment]


@app.callback([Output('piechart_1', 'figure'),
               Output('piechart_2', 'figure'),
               Output('my_datatable_1', 'data'),
               Output('my_h1', 'children')],
              [Input('my_dd_year', 'value'),
               Input('my_dd_month', 'value'),
               Input('my_dd_segment', 'value'), ]
              )
def update_graph(my_dd_year, my_dd_month, my_dd_segment):
    # check if select _all
    data_table = df_groupby.copy()
    if "Select All" in my_dd_year:
        data_table = data_table
    else:
        data_table = data_table[(data_table['YEAR'].isin(my_dd_year))]

    if "Select All" in my_dd_month:
        data_table = data_table
        month_ = f'{title_page} ' + ', '.join([month for month in lst_month])
        title_ = month_ + ' of ' + ', '.join([str(year) for year in lst_year])
        select_year = ', '.join([str(year) for year in lst_year])
    else:
        data_table = data_table[(data_table['MONTH'].isin(my_dd_month))]
        month_ = f'{title_page} ' + ', '.join([month for month in my_dd_month])
        title_ = month_ + ' of ' + ', '.join([str(year) for year in lst_year])
        select_year = ', '.join([str(year) for year in my_dd_year])

    data_table = data_table[(data_table['CLASS'] == 'Competitor')]

    if "Select All" in my_dd_segment:
        data_table = data_table
    else:
        data_table = data_table[(data_table['SEGMENT'].isin(my_dd_segment))]

    if "Select All" in my_dd_month:

        month_ = f'{title_page} ' + ', '.join([month for month in lst_month])
        title_ = month_ + ' of ' + ', '.join([str(year) for year in lst_year])
        select_year = ', '.join([str(year) for year in lst_year])
    else:
        month_ = f'{title_page} ' + ', '.join([month for month in lst_month])
        title_ = month_ + ' of ' + ', '.join([str(year) for year in lst_year])
        select_year = ', '.join([str(year) for year in my_dd_year])

    df_pivot = pd.pivot_table(data_table,
                              values=['VOLUME', 'TOTAL_AMT'],
                              index=['YEAR', 'MOTHER_BRAND'],
                              columns=['MONTH'],
                              aggfunc=['sum'],
                              fill_value=0
                              ).fillna(0).reset_index()

    df_pivot = lib.revert_month_pivot_table(df_pivot, [('', '', 'MOTHER_BRAND'), ('', '', 'YEAR')])
    df_pivot.columns = ['_'.join(str(s).strip() for s in col if s) for col in df_pivot.columns]
    for col_name in df_pivot.columns:
        if col_name.find('sum'):
            df_pivot.rename({col_name: col_name.replace('_sum', '')}, axis=1, inplace=True)

    # update_graph_1
    df_competitor1 = data_table.copy()
    sorted_df_competitor_top_10_vol = df_competitor1.sort_values("VOLUME", ascending=False)
    out_df_competitor_top_10_vol = sorted_df_competitor_top_10_vol.iloc[:11]
    out_df_competitor_top_10_vol = out_df_competitor_top_10_vol.append(
        {'MOTHER_BRAND': 'Others', 'VOLUME': sorted_df_competitor_top_10_vol['VOLUME'].iloc[11:].sum()},
        ignore_index=True,
    )

    df_graph_1 = out_df_competitor_top_10_vol

    pie_1 = px.pie(df_graph_1, values=df_graph_1['VOLUME'],
                   names=df_graph_1['MOTHER_BRAND'],
                   color_discrete_sequence=px.colors.sequential.Rainbow,
                   )
    # update_graph_2
    df_competitor2 = data_table.copy()
    # df_competitor2['TOTAL_AMT'] = pd.to_numeric(df_competitor2['TOTAL_AMT'], errors='coerce')
    sorted_df_competitor_top_10_amt = df_competitor2.sort_values("TOTAL_AMT", ascending=False)
    out_df_competitor_top_10_amt = sorted_df_competitor_top_10_amt.iloc[:11]
    out_df_competitor_top_10_amt = out_df_competitor_top_10_amt.append(
        {'MOTHER_BRAND': 'Others', 'TOTAL_AMT': sorted_df_competitor_top_10_amt['TOTAL_AMT'].iloc[11:].sum()},
        ignore_index=True,
    )
    df_graph_2 = out_df_competitor_top_10_amt
    pie_2 = px.pie(df_graph_2, values=df_graph_2['TOTAL_AMT'],
                   names=df_graph_2['MOTHER_BRAND'],
                   color_discrete_sequence=px.colors.sequential.Rainbow,

                   )
    pie_1.update_layout(
        title=dict(
            text=f'<b style="text-align:center;">Percent top 10 Voume in {month_} <br> of year: {select_year}',
            x=0.5,
            y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#638E9E'
            ),
        )
    )
    pie_2.update_layout(
        title=dict(
            text=f'<b style="text-align:center;">Percent top 10 Amount in {month_} <br> of year: {select_year}',
            x=0.5,
            y=0.95,
            font=dict(
                family="Arial",
                size=20,
                color='#2A63AB'
            ),
        )
    )
    return pie_1, pie_2, df_pivot.to_dict('records'), title_

