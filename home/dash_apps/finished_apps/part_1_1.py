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

#app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
df = read_xlsx.get_df()

df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
df['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')



#group data
df_group_qty = df.groupby(by=['Class','TAX_CODE','IMPORTER_NAME','YEAR','MONTH']).agg({'QTY':'sum'}).reset_index()
df_group_vol = df.groupby(by=['TAX_CODE']).agg({'VOLUME':'sum'}).reset_index()
df_group = df_group_qty.merge(df_group_vol, how = 'left', on = 'TAX_CODE')
df_group['QTY'] = df['QTY'].map('{:,.2f}'.format)
df_group['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
df_group['TOTAL_AMT'] = df['TOTAL_AMT'].map('${:,.2f}'.format)


#create pivot table
df_pivot = df_group[['IMPORTER_NAME','YEAR','MONTH','VOLUME','Class']]
df_pivot = pd.pivot_table(df_pivot,
                          values='VOLUME',
                          index=['YEAR', 'IMPORTER_NAME','Class'],
                          columns=['MONTH'],
                          aggfunc=['sum'],
                          #margins=True, margins_name='Grand Total',
                          ).fillna(0).reset_index()
df_pivot.columns = ['_'.join(str(s).strip() for s in col if s) for col in df_pivot.columns]
for col_name in df_pivot.columns:
    if col_name[:4] == 'sum_':
        df_pivot.rename({col_name:col_name[4:]}, axis=1, inplace=True)
#df_pivot['Grand Total'] = df_pivot['Grand Total'].map('{:,.2f}'.format)

# format


year_list = list(df_pivot['YEAR'].unique()) # lấy ra list năm để bỏ vào slider
class_list = list(df_pivot['Class'].unique())


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H5(f'Part 1.1: Importer Volume in Year {year_list[0]}', className='title_text'),
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
                                      for c in df_pivot['YEAR'].unique()]),
               html.P('CHỌN CLASS:'),
                dcc.Dropdown(id='select_class',
                             multi=False,
                             clearable=True,
                             disabled=False,
                             style={'display': True},
                             placeholder='CHỌN CLASS',
                             options=[{'label': c, 'value': c}
                                      for c in df_pivot['Class'].unique()]),
            ], className='adjust_drop_down_lists'),

        ], className="create_container2 six columns", style={'margin-bottom': '10px', "margin-top": "10px"}),

    ], className="row flex-display"),

    html.Div([
        html.Div([
            dt.DataTable(id='my_datatable',
                         columns=[{"name": i, "id": i} for i in df_pivot.columns],
                                style_data_conditional=(
                                     [
                                         {
                                             'if': {
                                                 'filter_query': '{{{}}} > {}'.format(col, value),
                                                 'column_id': col
                                             },
                                             'backgroundColor': '#3D9970',
                                             'color': 'white'
                                         } for (col, value) in df_pivot.quantile(0.1).iteritems()
                                     ] +
                                     [
                                         {
                                             'if': {
                                                 'filter_query': '{{{}}} <= {}'.format(col, value),
                                                 'column_id': col
                                             },
                                             'backgroundColor': '#FF4136',
                                             'color': 'white'
                                         } for (col, value) in df_pivot.quantile(0.5).iteritems()
                                     ]
                                    ),
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
    Output('select_class', 'value'),
    Input('select_class', 'options'))
def get_class_value(select_class):
    return [k['value'] for k in select_class][0]


@app.callback(Output('my_datatable', 'data'),
              [Input('select_year', 'value')],
              [Input('select_class', 'value')])
def display_table(select_year, select_class):
    data_table = df_pivot[
        (df_pivot['YEAR'] == select_year) & (df_pivot['Class'] == select_class)]
    return data_table.to_dict('records')


