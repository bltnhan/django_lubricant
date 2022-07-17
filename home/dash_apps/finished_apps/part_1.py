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
app.css.append_css({ "external_url" : "/static/css/s1.css" })


# app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets)


##DASH_VERSION =
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
#                 meta_tags=[{'name': 'viewport',
#                             'content': 'width=device-width, initial-scale=1.0'}]
#                 )
# app.config.suppress_callback_exceptions = True
# app.css.config.serve_locally = False

# get time update

data_path = 'home/dash_apps/finished_apps/data/data.xlsx'
oil_path = 'home/dash_apps/finished_apps/data/oil_application.xlsx'
m_time = os.path.getmtime(data_path)
date_time = datetime.datetime.fromtimestamp(m_time)
d = date_time.strftime("%m/%d/%Y, %H:%M:%S")

# call df
df = pd.read_excel(data_path, sheet_name="Vietnam", usecols='A:AJ')
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
df = df[['MONTH', 'YEAR', 'TAX_CODE', 'CLASS', 'IMPORTER_NAME', 'VOLUME', 'SEGMENT', 'TOTAL_AMT']]
df = df[(df['VOLUME'] != "UNSPECIFY") & (df['TOTAL_AMT'] != "UNSPECIFY")]
df['VOLUME'] = pd.to_numeric(df['VOLUME'], downcast="float")
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], downcast="float")
df['SEGMENT'] = df['SEGMENT'].replace('b2b', 'B2B')
# df['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
# df['TOTAL_AMT'] = df['TOTAL_AMT'].map('{:,.2f}'.format)

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

df_groupby = df.groupby(by=['YEAR', 'MONTH', 'TAX_CODE', 'IMPORTER_NAME', 'CLASS', 'SEGMENT']).agg(
    {'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()
# covert type du lieu
df_groupby['VOLUME'] = pd.to_numeric(df_groupby['VOLUME'], errors='coerce')
df_groupby['TOTAL_AMT'] = pd.to_numeric(df_groupby['TOTAL_AMT'], errors='coerce')

# title
title_page = 'Part 1: Importer Import Volume and Value'

app.layout = dbc.Container([
    # ----------------------------------------------------------------
    # Title, header
    dbc.Row([
        html.Meta(httpEquiv="refresh", content="360")
    ]),
    # dcc.Store stores the intermediate value
    dbc.Row([
        dbc.Col(
            html.H6(f'Last update on: {d}',
                    id='my_h6',
                    style={'text-align': 'left', 'font-decoration': 'italic', 'font-family': 'Arial'}
                    ))
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
    # -----------
    # Filter
    dbc.Row([
        dbc.Col([
            html.P('Select below options filters:',
                   style={'font-size': 13, 'font-family': 'Arial', 'color': '#007DBF', 'text-align': 'left'}),
            dcc.Dropdown(
                id='my_dd_year',
                multi=False,
                disabled=False,
                style={'display': True},
                placeholder='SELECT YEAR',
                # value = '2022',
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['YEAR'].unique())],
                className='drop-zone-dropdown'
            ),
            html.Br(),
            dcc.Dropdown(
                id='my_dd_month',
                multi=True,
                disabled=False,
                style={'display': True},
                placeholder='SELECT MONTH',
                # value = ['JAN'],
                clearable=True,
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['MONTH'].unique()) + ['Select All']],
                className='drop-zone-dropdown'
            ),
            html.Br(),
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
                className='drop-zone-dropdown',
            ),
            html.Br(),
            dcc.Dropdown(
                id='my_dd_segment', multi=True,
                # value = ['B2B'],
                clearable=True,
                placeholder='SELECT SEGMENT',
                options=[{'label': x, 'value': x}
                         for x in list(df_groupby['SEGMENT'].unique()) + ['Select All']],
                className='drop-zone-dropdown'
            ),

        ], className='g-2 align-self-start', style={"padding": "5px", "margin": "5px"}, width={"size": 2}
        ),

        dbc.Col([
            dbc.Row([
                dbc.Card([
                    dbc.CardBody(
                        html.H4(
                            "Total Volume(YTD)",
                            className="card-text text-primary font-bold-weight text-center",
                            style={"font-size": "Arial"})),
                    dbc.CardBody(
                        html.H1(
                            id='total_vol',
                            children="",
                            className="card-text text-danger font-bold-weight text-center",
                            style={"font-size": "80px", "font-size": "Arial"}),
                    )],
                    style={"width": "50rem", "height": "20rem", "border-radius": "10px", "padding": "5px",
                           "margin": "5px"},

                ),
                dbc.Card([
                    dbc.CardBody(
                        html.H4(
                            "Total Amount(YTD-USD)",
                            className="card-text text-primary font-bold-weight text-center",
                            style={"font-size": "Arial"})),
                    dbc.CardBody(
                        html.H1(
                            id='total_amount',
                            children="",
                            className="card-text text-danger font-bold-weight text-center",
                            style={"font-size": "80px", "font-size": "Arial"}),
                    )],
                    style={"width": "50rem", "height": "20rem", "border-radius": "10px", "padding": "5px",
                           "margin": "5px"},
                ),
            ], className='g-5'),
        ], width={'offset': 2})
    ]),
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
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Col([
                html.Div(id="main_datatable"),
            ], width={'size': 5}),
            html.Br(),
            html.Br(),
            html.Div([
                dcc.Dropdown(
                    id='my_dd_importer',
                    multi=True,
                    disabled=False,
                    style={'display': True, 'width': '500px', 'font-family': 'Arial'},
                    options=[{'label': x, 'value': x}
                             for x in list(df_groupby['IMPORTER_NAME'].unique()) + ['Select All']],
                    placeholder='SEARCH FOR IMPORTER NAME',
                    clearable=True,
                    className='dcc_compon'
                ),
            ], className="d-grid gap-5 d-md-block"),
            html.Br(),
            html.Div([
                dbc.Label("Show number of rows", style={'display': True, 'font-family': 'Arial'}),
                dcc.Dropdown(value=10, clearable=False, style={'width': '35%'},
                             options=[10, 25, 50, 100], id='row_drop'),
            ], className="drop-zone-dropdown", style={'display': True, 'font-family': 'Arial'}, ),
            html.Br(),
            dbc.Col([
                html.Div(id="detail_datatable"),
            ]),
        ], width={'size': 8}),
        dbc.Col([
            dbc.Row([
                dcc.Graph(id='my_pie_1', figure={}),
            ]),
            dbc.Row([
                dcc.Graph(id='my_pie_2', figure={}),
            ]),
            dcc.Store(id='store-data', data=[], storage_type='memory')
        ], width={'size': 4})
    ], align='top', justify='center', className='g-2'),
], fluid=True)


def clicked(ctx):
    if not ctx.triggered or not ctx.triggered[0]['value']:
        return None
    else:
        return ctx.triggered[0]['prop_id'].split('.')[0]


@app.callback(
    [Output('store-data', 'data'),
     Output('my_dd_importer', 'disabled'),
     Output('my_h1', 'children'), ],
    [Input('my_dd_year', 'value'),
     Input('my_dd_month', 'value'),
     Input('my_dd_class', 'value'),
     Input('my_dd_segment', 'value'),
     Input('my_dd_importer', 'value'), ]
)
def store_data(my_dd_year, my_dd_month, my_dd_class, my_dd_segment, my_dd_importer):
    dataset = df_groupby.copy()
    if my_dd_year is not None:
        dataset.loc[:] = dataset[dataset['YEAR'] == my_dd_year]
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

    if my_dd_importer is not None:

        if "Select All" in my_dd_importer:
            list_import = [x for x in list(df_groupby['IMPORTER_NAME'].unique())]
            dataset.loc[:] = dataset[dataset['IMPORTER_NAME'].isin(list_import)]
        else:
            dataset.loc[:] = dataset[dataset['IMPORTER_NAME'].isin(my_dd_importer)]
    else:
        dataset.loc[:] = dataset
    disabled_list = False
    return dataset.to_dict('records'), disabled_list, title_


@app.callback(
    Output('main_datatable', 'children'),
    Input('store-data', 'data'),
    prevent_initial_call=True,
)
def create_table_1(data):
    dff = pd.DataFrame(data)
    table_main = dff.groupby(by='CLASS').agg({'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()
    table_main = table_main.fillna(0)
    columns = []
    for col in table_main:
        if table_main[col].dtype == 'float64':
            if col == 'TOTAL_AMT':
                item = dict(id=col, name=col, type='numeric',
                            format=dict(specifier='$,.2f'))  # Example result 47,359.02
            elif col == 'YEAR':
                item = dict(id=col, name=col, type='numeric', format=dict(specifier=',.0f'))  # Example result 47,359
            else:
                item = dict(id=col, name=col, type='numeric', format=dict(specifier=',.2f'))
            columns.append(item)
        else:
            item = dict(id=col, name=col)
            columns.append(item)
    # table_main['VOLUME'] = table_main['VOLUME'].map('{:,.2f}'.format)
    # table_main['TOTAL_AMT'] = table_main['TOTAL_AMT'].map('${:,.2f}'.format)
    return dt.DataTable(
        data=table_main.to_dict('records'),
        columns=columns,
        style_cell={'textAlign': 'left',
                    'min-width': '100px',
                    'max-width': '100px',
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

        style_data={'color': 'black',
                    'border': '1px solid #00008B',
                    'textAlign': 'center'},
        style_data_conditional=(
                [
                    {
                        'if': {
                            'column_type': 'text'
                        },
                        'textAlign': 'left'
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
                +
                table_bars.data_bars(table_main, 'VOLUME', bar_color_1)
                +
                table_bars.data_bars(table_main, 'TOTAL_AMT', bar_color_2))
    )


@app.callback(
    [Output('detail_datatable', 'children'),
     Output('total_vol', 'children'),
     Output('total_amount', 'children'), ],
    [Input('store-data', 'data'),
    Input('row_drop', 'value')]
)
def create_table_2(data, row):
    dff = pd.DataFrame(data)
    table_detail = dff.copy()
    table_detail = table_detail.fillna(0)
    # table_detail = table_detail[table_detail['IMPORTER_NAME']!=0]

    vol = table_detail['VOLUME'].sum(axis=0)
    amount = table_detail['TOTAL_AMT'].sum(axis=0)
    vol = lib.human_format(vol)
    amount = lib.human_format(amount)
    amount = '$' + str(amount)

    table_detail = table_detail[(table_detail['IMPORTER_NAME'] != 0)].sort_values('TOTAL_AMT', ascending=False)
    table_detail['YEAR'] = table_detail['YEAR'].map(int)
    columns = []
    for col in table_detail:
        if table_detail[col].dtype == 'float64':
            if col == 'TOTAL_AMT':
                item = dict(id=col, name=col, type='numeric',
                            format=dict(specifier='$,.2f'))  # Example result 47,359.02
            elif col == 'YEAR':
                item = dict(id=col, name=col, type='numeric', format=dict(specifier=',.0f'))  # Example result 47,359
            else:
                item = dict(id=col, name=col, type='numeric', format=dict(specifier=',.2f'))

            columns.append(item)
        else:
            item = dict(id=col, name=col)
            columns.append(item)

    data_table = \
        dt.DataTable(
            data=table_detail.to_dict('records'),
            columns=columns,
            page_size=row,
            sort_action="native",
            style_table={"overflowX": "auto"},
            sort_mode="multi",
            # virtualization=True,
            style_cell={'min-width': '70px',
                        'max-width': '300px',
                        'backgroundColor': '',
                        'font-family': 'Arial',
                        },
            style_as_list_view=False,
            style_header={
                'backgroundColor': '#4DB299',
                'fontWeight': 'bold',
                'font': 'Arial',
                'textAlign': 'center',
                'color': 'white',
                'border': '1px solid #9A38D5'
            },

            style_data={
                'color': 'black',
                'border': '1px solid #00008B',
                'textAlign': 'center',
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '15px'},
            style_data_conditional=(
                    [
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
                    +
                    table_bars.data_bars(table_detail, 'VOLUME', bar_color_1)
                    +
                    table_bars.data_bars(table_detail, 'TOTAL_AMT', bar_color_2))
        )
    return data_table, vol, amount


@app.callback(
    [Output('my_pie_1', 'figure'),
     Output('my_pie_2', 'figure')],
    Input('store-data', 'data'),
)
def create_pie(data):
    dff = pd.DataFrame(data)
    table_detail = dff.copy()
    table_detail = table_detail.fillna(0)
    table_detail.loc[:] = table_detail.groupby(
        by=['YEAR', 'MONTH', 'TAX_CODE', 'IMPORTER_NAME', 'CLASS', 'SEGMENT']).agg(
        {'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()
    table_detail.loc[:] = table_detail[(table_detail['SEGMENT'] != 0)]
    select_year = ', '.join([str(year) for year in list(table_detail['YEAR'].unique())])
    month_ = ', '.join([str(month) for month in list(table_detail['MONTH'].unique())])
    fig_vol = px.pie(
        table_detail,
        names='SEGMENT',
        values='VOLUME',
        hole=0.7,
        color_discrete_sequence=px.colors.sequential.Turbo_r, )
    fig_amount = px.pie(
        table_detail,
        names='SEGMENT',
        values='TOTAL_AMT',
        hole=0.7,
        color_discrete_sequence=["#007DBF", "#0C7C59", "#004761", "#60BF8F", "#4DB299", "#3AA5A2", "#2697AC", "#138AB5",
                                 "#007DBF", "#266379", "#638E9E", "#2A63AB", "#0C3C80", "#001842"]
        , )

    fig_vol.update_layout(
        title=dict(
            text=f'<b style="text-align:center;">Vol by Segment in {month_} of year {select_year}',
            x=0.5,
            y=0.95,
            font=dict(
                family="Arial",
                size=14,
                color='#638E9E'
            ),
        )
    )
    fig_amount.update_layout(
        title=dict(
            text=f'<b style="text-align:center;">Amount by Segment in {month_} of year {select_year}',
            x=0.5,
            y=0.95,
            font=dict(
                family="Arial",
                size=14,
                color='#638E9E'
            ),
        )
    )
    return fig_vol, fig_amount


# ----------------------------------------------------------------
# Callbacks for search results


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

    list_file_names = ['home/dash_apps/finished_apps/data/data.xlsx', 'home/dash_apps/finished_apps/data/company_directory.xlsx', 'home/dash_apps/finished_apps/data/oil_application.xlsx',
                       'home/dash_apps/finished_apps/data/main_brand.xlsx']

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


if __name__ == '__main__':
    app.run_server(debug=True, port=3000)