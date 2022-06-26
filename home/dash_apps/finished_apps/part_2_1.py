import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.dash_table import DataTable, FormatTemplate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_table as dt
import dash_bootstrap_components as dbc
import pathlib
import urllib.request
import numpy as np
from . import read_xlsx

file_name = str(pathlib.Path(__file__).name)[:-3]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets)
app.css.append_css({ "external_url" : "/static/css/s1.css" })

df = read_xlsx.get_df()

df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
df['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')



#group data
df_group_2_1 = df.groupby(by=['CLASSIFICATION','INDUSTRY','YEAR','MONTH']).agg({'VOLUME':'sum','TOTAL_AMT':'sum'}).reset_index()
df_group_2_1['TOTAL_AMT'] = df_group_2_1['TOTAL_AMT'].map('${:,.2f}'.format)
df_group_2_1['CLASSIFICATION'].unique()

# df['QTY'] = df['QTY'].map('{:,.2f}'.format)
# df['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
# df['TOTAL_AMT'] = df['TOTAL_AMT'].map('${:,.2f}'.format)
# format
month_list = list(df_group_2_1['MONTH'].unique())
year_list = list(df_group_2_1['YEAR'].unique())
class_list = list(df_group_2_1['CLASSIFICATION'].unique())

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H5('Part 2A: Importer Industry Import Volume & Value', className='title_text'),
            ])
        ], className="title_container twelve columns")
    ], className="row flex-display"),

    html.Div([
        html.Div([
            html.Div([
                html.P('CHỌN CLASSIFICATION:'),
                dcc.Checklist(id='select_classification',
                              style={'display': True},
                              options=[{'label': c, 'value': c}
                                       for c in df_group_2_1['CLASSIFICATION'].unique()]),
                html.P('CHỌN NĂM:'),
                dcc.Dropdown(id='select_year',
                             multi=False,
                             clearable=True,
                             disabled=False,
                             style={'display': True},
                             value='2022',
                             placeholder='CHỌN NĂM',
                             options=[{'label': c, 'value': c}
                                      for c in df_group_2_1['YEAR'].unique()]),

                html.P('CHỌN THÁNG:'),
                dcc.Checklist(id='select_month',
                              style={'display': True},
                              options=[{'label': c, 'value': c}
                                       for c in df_group_2_1['MONTH'].unique()]

                              )
            ], className='adjust_drop_down_lists'),

        ], className="create_container2 four columns"),
        html.Div([
            dt.DataTable(id='my_datatable',
                         columns=[{'name': i, 'id': i} for i in
                                  df_group_2_1.loc[:, ['CLASSIFICATION', 'INDUSTRY', 'VOLUME', 'TOTAL_AMT']]],
                         sort_action="native",
                         style_table={"overflowX": "auto"},
                         sort_mode="multi",
                         virtualization=True,
                         style_cell={'textAlign': 'left',
                                     'min-width': '100px',
                                     'backgroundColor': '#F2F2F2',
                                     'font-family': 'Arial',
                                     },
                         style_as_list_view=False,
                         style_header={
                             'backgroundColor': '#16a085',
                             'fontWeight': 'bold',
                             'font': 'Times New Roman',
                             'color': 'white',
                             'border': '1px solid #9A38D5'
                         },
                         style_data={'textOverflow': 'hidden', 'color': 'black',
                                     'border': '1px solid orange'},
                         fixed_rows={'headers': True},
                         )

        ], className='create_container2 eight columns'),
    ], className="row flex-display"),

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})


@app.callback(
    Output('select_year', 'value'),
    Input('select_year', 'options'))
def get_year_value(select_year):
    return [k['value'] for k in select_year][0]


@app.callback(
    Output('select_month', 'value'),
    Input('select_month', 'options'))
def get_month_value(select_month):
    return select_month


@app.callback(
    Output('select_classification', 'value'),
    Input('select_classification', 'options'))
def get_class_value(select_classification):
    return select_classification


@app.callback(Output('my_datatable', 'data'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')],
              [Input('select_classification', 'value')])
def display_table(select_year, select_month, select_classification):
    data_table = df_group_2_1[(df_group_2_1['YEAR'] == select_year) & df_group_2_1['MONTH'].isin(select_month) \
                              & df_group_2_1['CLASSIFICATION'].isin(select_classification)]
    return data_table.to_dict('records')



