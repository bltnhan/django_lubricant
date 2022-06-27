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



# pivot
df_pivot_2 = df[['INDUSTRY','TOTAL_AMT','YEAR','MONTH']]
df_pivot_2['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='ignore')

df_result = pd.pivot_table(df_pivot_2,
                          values='TOTAL_AMT',
                          index=['YEAR','INDUSTRY'],
                          columns=['MONTH'],
                          aggfunc= ['sum'],
                          fill_value = 0
                          ).fillna(0).reset_index()
df_result.columns = ['_'.join(str(s).strip() for s in col if s) for col in df_result.columns]
for col_name in df_result.columns:
    if col_name[:4] == 'sum_':
        df_result.rename({col_name:col_name[4:]}, axis=1, inplace=True)
        df_result[col_name[4:]] = df_result[col_name[4:]].map('${:,.2f}'.format)

year_list = list(df_result['YEAR'].unique())


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H5(f'Part 2B: Import share by sector by month in {year_list[0]}', className='title_text'),
            ])
        ], className="title_container twelve columns")
    ], className="row flex-display"),

    html.Div([
        html.Div([
            html.Div([
                html.P('CHỌN NĂM:'),
                dcc.Dropdown(id='select_year',
                             multi=False,
                             clearable=True,
                             disabled=False,
                             style={'display': True},
                             value='2022',
                             placeholder='CHỌN NĂM',
                             options=[{'label': c, 'value': c}
                                      for c in df_result['YEAR'].unique()])
            ], className='adjust_drop_down_lists'),

        ], className="create_container2 four columns", style={'margin-bottom': '10px', "margin-top": "10px"}),

    ], className="row flex-display"),

    html.Div([
        html.Div([
            dt.DataTable(id='my_datatable',
                         columns=[{"name": i, "id": i} for i in df_result.columns],

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

        ], className='create_container2 twelve columns'),

    ], className="row flex-display"),

], id="mainContainer", style={"display": "flex", "flex-direction": "column"})


@app.callback(
    Output('select_year', 'value'),
    Input('select_year', 'options'))
def get_year_value(select_year):
    return [k['value'] for k in select_year][0]


@app.callback(Output('my_datatable', 'data'),
              [Input('select_year', 'value')])
def display_table(select_year):
    data_table = df_result[
        (df_result['YEAR'] == select_year)]
    return data_table.to_dict('records')