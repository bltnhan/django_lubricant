import dash
from dash import dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.dash_table import DataTable, FormatTemplate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
from dash import dash_table as dt
import dash_bootstrap_components as dbc
import pathlib
import urllib.request
import numpy as np
from . import lib, table_bars
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

# app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets)
# app.css.append_css({ "external_url" : "/static/css/s1.css" })



#get time update
data_path = 'home/dash_apps/finished_apps/data/data.xlsx'
oil_path = 'home/dash_apps/finished_apps/data/oil_application.xlsx'
m_time = os.path.getmtime(data_path)
date_time = datetime.datetime.fromtimestamp(m_time)
d = date_time.strftime("%m/%d/%Y, %H:%M:%S")

# call df
df = pd.read_excel(data_path, sheet_name=0, usecols='A:AJ')
# df_oil = pd.read_excel(oil_path, sheet_name=0, usecols= 'A:E')
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
df = df[['MONTH', 'YEAR', 'TAX_CODE', 'CLASS', 'IMPORTER_NAME', 'VOLUME', 'SEGMENT', 'TOTAL_AMT', 'INDUSTRY']]
df = df[(df['VOLUME'] != "UNSPECIFY") & (df['TOTAL_AMT'] != "UNSPECIFY")]
df['VOLUME'] = pd.to_numeric(df['VOLUME'], downcast="float")
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], downcast="float")
df['SEGMENT'] = df['SEGMENT'].replace('b2b', 'B2B')
df['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
df['TOTAL_AMT'] = df['TOTAL_AMT'].map('{:,.2f}'.format)
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

df_groupby = df.groupby(by=['YEAR', 'MONTH', 'TAX_CODE', 'IMPORTER_NAME', 'CLASS', 'SEGMENT', 'INDUSTRY']).agg(
    {'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()

# covert type du lieu

df_groupby['VOLUME'] = pd.to_numeric(df_groupby['VOLUME'], errors='coerce')
df_groupby['TOTAL_AMT'] = pd.to_numeric(df_groupby['TOTAL_AMT'], errors='coerce')

# title
title_page = 'Part 2B: Import share by sector by month'

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
                value=['1-COMPETITOR'],
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['CLASS'].unique()) + ['Select All']],
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

        ], className='g-2 align-self-start', style={"padding": "5px", "margin": "5px"}, width={"size": 2}
        ),

        # ----------------------------------------------------------------
        # Card
        dbc.Col([
            dbc.Row([
                dbc.Card([
                    dbc.CardBody(
                        html.H4(
                            "Top Industry Import (YTD)",
                            className="card-text text-primary font-bold-weight text-center"),
                        style={"font-family": "Arial"}),
                    dbc.CardBody(
                        html.H1(
                            id='top_vol',
                            children="",
                            className="card-text text-danger font-bold-weight text-center",
                            style={"font-size": "80px", "font-family": "Arial"}),
                    )],
                    style={"width": "50rem", "height": "20rem", "border-radius": "10px", "padding": "5px",
                           "margin": "5px"},

                ),
                dbc.Card([
                    dbc.CardBody(
                        html.H4(
                            "Select Option below to view share by Amount/Vol",
                            className="card-text text-primary font-bold-weight text-center"),
                        style={'font-family': 'Arial'}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Sum Amount",
                                id='sum-amount-btn',
                                color="success",
                                className='me-2 btn btn-outline-light',
                                style={'height': '50px', 'font-size': '12px', 'font-family': 'Arial'},
                                n_clicks_timestamp='0'
                            )], width={'offset': 2}),
                        dbc.Col([
                            dbc.Button(
                                "Sum Volume",
                                id='sum-volume-btn',
                                color="primary",
                                className='me-2 btn btn-outline-light',
                                style={'height': '50px', 'font-size': '12px', 'font-family': 'Arial'},
                                n_clicks_timestamp='0'
                            ),
                        ], width={'offset': 2})

                    ], )
                ],
                    style={"width": "50rem", "height": "20rem", "border-radius": "10px", "padding": "5px",
                           "margin": "5px"},
                ),

            ], className='g-5')
        ])
    ]),
    html.Br(),
    html.Br(),
    # ----------------------------------------------------------------
    # Download button
    dbc.Row([
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
    dbc.Row([
        dbc.Col([
            dbc.Col([
                dt.DataTable(
                    id='my_datatable_1',
                    # columns=[{'name': i, 'id': i} for i in
                    #         df_groupby.loc[:, ['TAX_CODE','IMPORTER_NAME', 'VOLUME', 'TOTAL_AMT']]],
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

        ], width={'size': 8}),
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


@app.callback(
    Output('my_dd_class', 'value'),
    Input('my_dd_class', 'options'))
def get_class_value(my_dd_class):
    return [k['value'] for k in my_dd_class]


@app.callback(
    Output('my_dd_segment', 'value'),
    Input('my_dd_segment', 'options'))
def get_segment_value(my_dd_segment):
    return [k['value'] for k in my_dd_segment]


@app.callback(
    [Output('top_vol', 'children'),
     Output('my_datatable_1', 'data'),
     Output('my_h1', 'children')],
    [Input('sum-amount-btn', 'n_clicks_timestamp'),
     Input('sum-volume-btn', 'n_clicks_timestamp'),
     Input('my_dd_year', 'value'),
     Input('my_dd_month', 'value'),
     Input('my_dd_class', 'value'),
     Input('my_dd_segment', 'value'), ]
)
def update_graph(amount_btn, volume_btn, my_dd_year, my_dd_month, my_dd_class, my_dd_segment):
    # check if select _all
    data_table = df_groupby.copy()
    if "Select All" in my_dd_year:
        data_table = data_table
    else:
        data_table = data_table[(data_table['YEAR'].isin(my_dd_year))]

    if "Select All" in my_dd_month:
        data_table = data_table
        title_ = f'{title_page} ' + ', '.join([month for month in lst_month])
        title_ = title_ + ' of ' + ', '.join([str(year) for year in lst_year])
    else:
        data_table = data_table[(data_table['MONTH'].isin(my_dd_month))]
        title_ = f'{title_page} ' + ', '.join([month for month in my_dd_month])
        title_ = title_ + ' of ' + ', '.join([str(year) for year in lst_year])

    if "Select All" in my_dd_class:
        data_table = data_table
    else:
        data_table = data_table[(data_table['CLASS'].isin(my_dd_class))]

    if "Select All" in my_dd_segment:
        data_table = data_table
    else:
        data_table = data_table[(data_table['SEGMENT'].isin(my_dd_segment))]

    if "Select All" in my_dd_month:

        title_ = f'{title_page} ' + ', '.join([month for month in lst_month])
        title_ = title_ + ' of ' + ', '.join([str(year) for year in lst_year])
    else:
        title_ = f'{title_page} ' + ', '.join([month for month in my_dd_month])
        title_ = title_ + ' of ' + ', '.join([str(year) for year in lst_year])
    if int(amount_btn) > int(volume_btn):
        df_result_vol = pd.pivot_table(data_table,
                                       values='VOLUME',
                                       index=['YEAR', 'INDUSTRY'],
                                       columns=['MONTH'],
                                       aggfunc=['sum'],
                                       fill_value=0
                                       ).fillna(0).reset_index()
        lib.rename_pivot_column(df_result_vol, False)
        top_vol = data_table['VOLUME'].nlargest(1).values[0]
        title_ = title_ + ' by Volume'
    else:
        df_result_vol = pd.pivot_table(data_table,
                                       values='TOTAL_AMT',
                                       index=['YEAR', 'INDUSTRY'],
                                       columns=['MONTH'],
                                       aggfunc=['sum'],
                                       fill_value=0
                                       ).fillna(0).reset_index()
        lib.rename_pivot_column(df_result_vol, False)
        top_vol = data_table['TOTAL_AMT'].nlargest(1).values[0]
        title_ = title_ + ' by Amount'

    top_vol = lib.human_format(top_vol)

    lib.format_percent_df(df_result_vol, 2, ['YEAR', 'INDUSTRY'])
    df_result_vol = lib.revert_month(df_result_vol, list(df_result_vol.columns), ['YEAR', 'INDUSTRY'])

    df_result_vol = df_result_vol.drop(columns=['YEAR'], axis=1)
    return top_vol, df_result_vol.to_dict('records'), title_


# ----------------------------------------------------------------
# Callbacks progress_Bar
@app.callback(
    Output('progress_bar', 'value'),
    Input('clock', 'n_intervals'))
def progress_bar_update(n):
    global progress_memeory
    if not progress_queue.empty():
        progress_bar_val = progress_queue.get()
        progress_memeory = progress_bar_val
    else:
        progress_bar_val = progress_memeory
    return (progress_bar_val,)


@app.callback([
    Output("start_work", "n_clicks")],
    [Input("start_work", "n_clicks")])
def start_bar(n):
    if n == 0:
        return (0,)
    threading.Thread(target=start_work, args=(progress_queue,)).start()
    return (0,)


def start_work(output_queue):
    list_links = [
        "https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107257&ithint=file%2cxlsx&authkey=!AMISo-nz92nMhpA",
        'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107216&ithint=file%2cxlsx&authkey=!AFWwzx98ryaPkig',
        'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107098&ithint=file%2cxlsx&authkey=!AFjg9MHgv4VRIqI',
        'https://onedrive.live.com/download.aspx?resid=C43234B4367095E1!107220&ithint=file%2cxlsx&authkey=!ALjBwbSqS6TYXn4'
    ]
    list_file_names = ['data/data.xlsx', 'data/company_directory.xlsx', 'data/oil_application.xlsx',
                       'data/main_brand.xlsx']

    for link in list_links:
        with open(list_file_names[list_links.index(link)], "wb") as f:
            response = requests.get(link, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
                i = 0
                while i < 101:
                    time.sleep(0.1)
                    if output_queue.empty():
                        output_queue.put(i)
                    i += 1
    return (None)


