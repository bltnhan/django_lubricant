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
from dash_table.Format import Format, Scheme
import plotly.express as px
from. import table_bars
from. import lib
import urllib.request
import requests
import datetime
import os
import sys
from queue import Queue
import threading
import time
from datetime import datetime
pd.options.display.float_format = '${:.2f}'.format
# from dash.dash import no_update
# from dash.exceptions import PreventUpdate
bar_color_1 = "#60BF8F"
bar_color_2 = "#4C97BF"
progress_queue = Queue(1)
progress_memeory = 0


# DJANGO_VERSION
file_name = str(pathlib.Path(__file__).name)[:-3]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets, add_bootstrap_links=True)
app.css.append_css({"external_url": "/static/css/s1.css"})

# app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets)
# app.css.append_css({ "external_url" : "/static/css/s1.css" })


# get time update
data_path = 'home/dash_apps/finished_apps/data/data.pkl'
oil_path = 'home/dash_apps/finished_apps/data/oil_application.xlsx'
m_time = os.path.getmtime(data_path)
date_time = datetime.fromtimestamp(m_time)
d = date_time.strftime("%m/%d/%Y, %H:%M:%S")

# call df
# df = pd.read_excel(demo_path, sheet_name="Vietnam", usecols= 'A:AJ')
df = pd.read_pickle(data_path)
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
df = df[['MONTH', 'YEAR', 'CLASS', 'MOTHER_BRAND', 'VOLUME', 'TOTAL_AMT', 'OIL_APPLICATION_CHECK']]
df = df.merge(df_oil, left_on='OIL_APPLICATION_CHECK', right_on='CODE', suffixes=(False, False))
df = df[['MONTH', 'YEAR', 'CLASS', 'SEGMENT', 'MOTHER_BRAND', 'VOLUME', 'TOTAL_AMT', 'OIL_APPLICATION_CHECK',
         'OIL APPLICATION (ENGLISH)']]
df['SEGMENT'] = df['SEGMENT'].replace('b2b', 'B2B')
df.rename(columns={'OIL APPLICATION (ENGLISH)': 'TYPE_OF_OIL'}, inplace=True)
# ----------------------------------------------------------------
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

# ----------------------------------------------------------------
# covert type du lieu
df = df[(df['VOLUME'] != "UNSPECIFY") & (df['TOTAL_AMT'] != "UNSPECIFY")]
df['VOLUME'] = pd.to_numeric(df['VOLUME'], downcast="float")
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], downcast="float")
df['VOLUME'] = df['VOLUME'].fillna(0)
df['TOTAL_AMT'] = df['TOTAL_AMT'].fillna(0)
# df['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
# df['TOTAL_AMT'] = df['TOTAL_AMT'].map('{:,.2f}'.format)
df_groupby = df.groupby(by=['MONTH', 'YEAR', 'CLASS', 'SEGMENT', 'MOTHER_BRAND', 'TYPE_OF_OIL']).agg(
    {'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()
df_groupby['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df_groupby['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')

# title
title_page = 'Part 3A: Imported product volume share in '

# ----------------------------------------------------------------
# layout
app.layout = dbc.Container([
    # ----------------------------------------------------------------
    # Title, header
    dbc.Row([
        html.Meta(httpEquiv="refresh", content="360")
    ]),
    dbc.Row([
        dbc.Col(
            html.H6(f'Last update on: {d}',
                    id='my_h6',
                    style={'text-align': 'left', 'font-decoration': 'italic', 'font-family': 'Arial'}
                    ))
    ]),
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
        dbc.Col(
            html.H2(children=
                    title_page,
                    id='my_h1',
                    className='text-center text-success, mb-4'),
            style={'font-family': 'Arial'},
            width=12)
    ]),
    # ----------------------------------------------------------------
    # Filter
    dbc.Row([
        html.P('Select below options filters:',
               style={'font-size': 13, 'font-family': 'Arial', 'color': '#007DBF', 'text-align': 'left'}),
    ]),
    dbc.Row([

        dbc.Col([
            dcc.Dropdown(
                id='my_dd_year',
                multi=False, value='2022',
                # disabled=False,
                style={'display': True},
                placeholder='SELECT YEAR',
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['YEAR'].unique())],
                className='dcc-compon'
            ),
        ], width={'size': 2}),
        dbc.Col([
            dcc.Dropdown(
                id='my_dd_month',
                multi=True, value=['JAN'],
                disabled=False,
                style={'display': True},
                placeholder='SELECT MONTH',
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['MONTH'].unique()) + ['Select All']],
                className='dcc-compon'
            ),
        ], width={'size': 2}),
        dbc.Col([
            dcc.Dropdown(
                id='my_dd_class',
                multi=True,
                disabled=False,
                style={'display': True},
                placeholder='SELECT CLASS',
                # value = ['Competitor'],
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['CLASS'].unique()) + ['Select All']],
                className='dcc-compon',
            ),
        ], width={'size': 2}),
        dbc.Col([
            dcc.Dropdown(
                id='my_dd_segment', multi=True,
                # value = ['B2B'],
                clearable=True,
                placeholder='SELECT SEGMENT',
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['SEGMENT'].unique()) + ['Select All']],
                className='dcc-compon'
            ),
        ], width={'size': 2}),

    ], className='g-2 align-self-start', style={"padding": "5px", "margin": "5px"}),
    # ----------------------------------------------------------------
    # Opional Sum
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    html.H4(
                        "Select Option Volume Share by Type of Oil or Brand Name",
                        style={'font-family': 'Arial'},
                        className="card-text text-info font-bold-weight text-center")),
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "Type of Oil",
                            id='sum-amount-btn',
                            color="success",
                            className='me-2 btn btn-outline-light',
                            style={'height': '50px', 'font-size': '12px', 'font-family': 'Arial', },
                            n_clicks_timestamp='0'
                        )], width={'offset': 2}),
                    dbc.Col([
                        dbc.Button(
                            "Brand Name",
                            id='sum-volume-btn',
                            color="primary",
                            className='me-2 btn btn-outline-light',
                            style={'height': '50px', 'font-size': '12px', 'font-family': 'Arial', },
                            n_clicks_timestamp='0'
                        ),
                    ], width={'offset': 2})

                ], )
            ],
                style={"width": "50rem", "height": "20rem", "border-radius": "10px", "padding": "5px", "margin": "5px"},
            ),
        ]),
    ], align='top', justify='center', className='g-2'),
    dbc.Row([
        dbc.Col([
            html.H4(
                id='my_h4',
                children=[],
                style={'font-family': 'Arial'},
                className="card-text text-primary font-bold-weight text-center"),
            html.Div([
                dbc.Label("Show number of rows", style={'display': True, 'font-family': 'Arial'}),
                dcc.Dropdown(value=10, clearable=False, style={'width': '35%'},
                             options=[10, 25, 50, 100], id='row_drop'),
            ], className="drop-zone-dropdown", style={'display': True, 'font-family': 'Arial'}, ),
            html.Div(id='my_datatable', ),
            dcc.Store(id='store-data', data=[], storage_type='memory')
        ], width={'size': 8}),
    ])
], fluid=True)


# ----------------------------------------------------------------
# Callbacks day/month/class/segment

# ----------------------------------------------------------------
# Callbacks main
@app.callback(
    [Output('store-data', 'data'),
     Output('my_h1', 'children'), ],
    [Input('my_dd_year', 'value'),
     Input('my_dd_month', 'value'),
     Input('my_dd_class', 'value'),
     Input('my_dd_segment', 'value'), ]
)
def store_data(my_dd_year, my_dd_month, my_dd_class, my_dd_segment):
    dataset = df_groupby.copy()
    if my_dd_year is not None:
        dataset.loc[:] = dataset[dataset['YEAR'] == my_dd_year]

    else:
        dataset.loc[:] = dataset
    if my_dd_month is not None:
        if "Select All" in my_dd_month:
            dataset = dataset
            month_ = f'{title_page} ' + ', '.join([month for month in lst_month])
            title_ = month_ + ' of ' + ', '.join([str(year) for year in lst_year])
        else:
            dataset.loc[:] = dataset[(dataset['MONTH'].isin(my_dd_month))]
            month_ = f'{title_page} ' + ', '.join([month for month in my_dd_month])
            title_ = month_ + ' of ' + ', '.join([str(year) for year in lst_year])
    else:
        dataset.loc[:] = dataset
        title_ = title_page + ' of ' + ', '.join([str(year) for year in lst_year])

    if my_dd_class is not None:
        if "Select All" in my_dd_class:
            dataset = dataset
        else:
            dataset.loc[:] = dataset[(dataset['CLASS'].isin(my_dd_class))]
    else:
        dataset.loc[:] = dataset

    if my_dd_segment is not None:
        if "Select All" in my_dd_segment:
            dataset = dataset
        else:
            dataset.loc[:] = dataset[(dataset['SEGMENT'].isin(my_dd_segment))]
    else:
        dataset.loc[:] = dataset

    return dataset.to_dict('records'), title_


@app.callback(
    [Output('my_datatable', 'children'),
     Output('my_h4', 'children'), ],
    [Input('store-data', 'data'),
     Input('my_dd_month', 'value'),
     Input('sum-amount-btn', 'n_clicks_timestamp'),
     Input('sum-volume-btn', 'n_clicks_timestamp'),
     Input('row_drop', 'value')],

)
def update_graph(data, my_dd_month, amount_btn, volume_btn, row_v):
    dff = pd.DataFrame(data)
    data_ = dff.copy()

    if int(amount_btn) > int(volume_btn):
        option_ = f'by TYPE OF OIL'
        df_result_val = pd.pivot_table(data_,
                                       values='VOLUME',
                                       index=['YEAR', 'TYPE_OF_OIL', ],
                                       columns=['MONTH'],
                                       aggfunc=['sum'],
                                       fill_value=0
                                       ).fillna(0).reset_index()
        lib.rename_pivot_column(df_result_val, False)
        lib.format_percent_df(df_result_val, 2, ['YEAR', 'TYPE_OF_OIL'])
        df_result_val = lib.revert_month(df_result_val, list(df_result_val.columns), ['YEAR', 'TYPE_OF_OIL'])

    else:
        option_ = f'by BRAND NAME'
        df_result_val = pd.pivot_table(data_,
                                       values='VOLUME',
                                       index=['YEAR', 'MOTHER_BRAND', ],
                                       columns=['MONTH'],
                                       aggfunc=['sum'],
                                       fill_value=0
                                       ).fillna(0).reset_index()
        lib.rename_pivot_column(df_result_val, False)
        lib.format_percent_df(df_result_val, 2, ['YEAR', 'MOTHER_BRAND'])
        df_result_val = lib.revert_month(df_result_val, list(df_result_val.columns), ['YEAR', 'MOTHER_BRAND'])
    df_result_val = df_result_val.drop(columns=['YEAR'], axis=1)

    # -------------------------------
    # format column
    columns = []
    # format percentage, money
    money = FormatTemplate.money(2)
    percentage = FormatTemplate.percentage(2)
    for col in df_result_val:
        if df_result_val[col].dtype == 'float64':
            item = dict(id=col, name=col, type='numeric', format=percentage)
            columns.append(item)
        else:
            item = dict(id=col, name=col)
            columns.append(item)
            condition_format = [
                {
                    'if': {'column_id': 'YEAR'},
                    'width': '70px'
                },
                {
                    'if': {'column_id': 'IMPORTER_NAME'},
                    'width': '250px'
                },
                {
                    'if': {
                        'column_type': 'text'
                    },
                    'textAlign': 'left'
                },
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {
                        'column_type': 'numeric'
                    },
                    'textAlign': 'right'
                },
                {
                    'if': {
                        'column_id': 'VOLUME',
                    },
                    'textAlign': 'right',
                },
            ]
    if my_dd_month is not None:
        if "Select All" in my_dd_month:
            # for month in lst_month:
                # condition_format = condition_format + table_bars.data_bars(df_result_val, month, bar_color_1)
            title_table = ', '.join([month for month in lst_month])


        else:
            #for month in my_dd_month:
                # condition_format = condition_format + table_bars.data_bars(df_result_val, month, bar_color_1)
            title_table = ', '.join([month for month in my_dd_month])
    else:
        for month in lst_month:
            condition_format = condition_format + table_bars.data_bars(df_result_val, month, bar_color_1)
        title_table = ', '.join([month for month in lst_month])

    table_amt = dt.DataTable(
        data=df_result_val.to_dict('records'),
        columns=columns,
        page_size=row_v,
        sort_action="native",
        style_cell={
            'textAlign': 'left',
            'min-width': '70px',
            'max-width': '200px',
            'backgroundColor': '',
            'font-family': 'Arial',
        },
        style_header={
            'backgroundColor': '#2A63AB',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'font': 'Arial',
            'color': 'white',
            'border': '1px solid 004761'
        },

        style_data={
            'color': 'black',
            'border': '1px solid #00008B',
            'whiteSpace': 'normal',
            'width': 'auto',
            'height': 'auto',
            'lineHeight': '15px'},
        style_data_conditional=condition_format
    )

    title_table = f"Data Table {option_} in " + title_table
    return table_amt, title_table


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
