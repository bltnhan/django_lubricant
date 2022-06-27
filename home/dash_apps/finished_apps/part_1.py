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
from . import read_xlsx
import urllib.request
from calendar import month_name
import datetime
pd.options.display.float_format = '${:,.2f}'.format


file_name = str(pathlib.Path(__file__).name)[:-3]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash(f'{file_name}', external_stylesheets=external_stylesheets)
app.css.append_css({ "external_url" : "/static/css/s1.css" })

#app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

df = read_xlsx.get_df()

#group data
df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
df['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')

df_group_qty = df.groupby(by=['Class','TAX_CODE','IMPORTER_NAME','YEAR','MONTH']).agg({'QTY':'sum'}).reset_index()
df_group_vol = df.groupby(by=['TAX_CODE']).agg({'VOLUME':'sum'}).reset_index()
df_group = df_group_qty.merge(df_group_vol, how = 'left', on = 'TAX_CODE')

df_group['QTY'] = df['QTY'].map('{:,.2f}'.format)
df_group['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
df_group['TOTAL_AMT'] = df['TOTAL_AMT'].map('${:,.2f}'.format)

#create list
year_list = list(df['YEAR'].unique()) # lấy ra list năm để bỏ vào slider

month_list = list(df['MONTH'].unique())
months_dict = {}
for i in range(1,13):
    months_dict[datetime.date(2020, i, 1).strftime('%b').title()] = i
month_list = sorted(month_list, key=lambda x: months_dict[x.title()])


class_list = list(df['Class'].unique())

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H5('Part 1: Importer Import Volume & Value', className='title_text'),
            ])
        ], className="title_container twelve columns")
    ], className="row flex-display"),

    html.Div([
        html.Div([
            html.Div([
                html.P('Select Year:'),
                dcc.Dropdown(id='select_year',
                             multi=False,
                             clearable=True,
                             disabled=False,
                             style={'display': True},
                             value='2022',
                             placeholder='CHỌN NĂM',
                             options=[{'label': c, 'value': c}
                                      for c in df_group['YEAR'].unique()]),
                html.P('Select Month:'),
                dcc.Dropdown(id='select_month',
                             multi=False,
                             clearable=True,
                             disabled=False,
                             style={'display': True},
                             placeholder='CHỌN THÁNG',
                             options=[{'label': c, 'value': c}
                                      for c in month_list]),
                html.P('CHỌN CLASS:'),
                dcc.Dropdown(id='select_class',
                             multi=False,
                             clearable=True,
                             disabled=False,
                             style={'display': True},
                             placeholder='CHỌN CLASS',
                             options=[{'label': c, 'value': c}
                                      for c in df_group['Class'].unique()]),
            ], className='adjust_drop_down_lists'),

        ], className="create_container2 six columns", style={'margin-bottom': '10px', "margin-top": "10px"}),

    ], className="row flex-display"),

    html.Div([

        html.Div([
            dt.DataTable(id='my_datatable',
                         columns=[{'name': i, 'id': i} for i in
                                  df_group.loc[:, ['Class', 'TAX_CODE', 'IMPORTER_NAME',
                                                   'QTY', 'VOLUME']]],
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


@app.callback(
    Output('select_month', 'value'),
    Input('select_month', 'options'))
def get_month_value(select_month):
    return [k['value'] for k in select_month][0]


@app.callback(
    Output('select_class', 'value'),
    Input('select_class', 'options'))
def get_class_value(select_class):
    return [k['value'] for k in select_class][0]


@app.callback(Output('my_datatable', 'data'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')],
              [Input('select_class', 'value')])
def display_table(select_year, select_month, select_class):
    data_table = df_group[
        (df_group['YEAR'] == select_year) & (df_group['MONTH'] == select_month) & (df_group['Class'] == select_class)]
    return data_table.to_dict('records')



