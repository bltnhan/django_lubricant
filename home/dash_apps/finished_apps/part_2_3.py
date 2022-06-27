import dash
import dash_core_components as dcc
import dash_html_components as html
from turtle import ht
import plotly.express as px
from dash.dependencies import Input, Output
from dash.dash_table import DataTable, FormatTemplate
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_table as dt
import dash_bootstrap_components as dbc
import pathlib
import datetime
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
df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
df['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')
df[['QTY','VOLUME','TOTAL_AMT']] = df[['QTY','VOLUME','TOTAL_AMT']].replace('UNSPECIFY',0)
df[['QTY','VOLUME','TOTAL_AMT']] = df[['QTY','VOLUME','TOTAL_AMT']].fillna(0)
df['QTY'] = df['QTY'].map('{:,.2f}'.format)
df['VOLUME'] = df['VOLUME'].map('{:,.2f}'.format)
df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce')
df['VOLUME'] = pd.to_numeric(df['VOLUME'], errors='coerce')
df['TOTAL_AMT'] = pd.to_numeric(df['TOTAL_AMT'], errors='coerce')
df_competitor = df[df['Class']=='Competitor']
df_competitor = df_competitor.groupby(by=['YEAR','MONTH','MOTHER_BRAND']).agg({'VOLUME':'sum','TOTAL_AMT':'sum'}).reset_index()

year_list = list(df_competitor['YEAR'].unique())
month_list = list(df_competitor['MONTH'].unique())
months_dict = {}
for i in range(1, 13):
    months_dict[datetime.date(2020, i, 1).strftime('%b').title()] = i
month_list = sorted(month_list, key=lambda x: months_dict[x.title()])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H5(f'Part 2C: Import share by competitor by month in {year_list[0]}', className='title_text'),
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
                             placeholder='Select Year',
                             options=[{'label': c, 'value': c}
                                      for c in df_competitor['YEAR'].unique()])
            ], className='adjust_drop_down_lists'),

            html.Div([
                html.P('Select Month:'),
                dcc.Checklist(id='select_month',
                              style={'display': True},
                              options=[{'label': c, 'value': c}
                                       for c in month_list])
            ], className='adjust_drop_down_lists'),

        ], className="create_container2 four columns", style={'margin-bottom': '10px', "margin-top": "10px"}),

    ], className="row flex-display"),

    html.Div([
        html.Div([
            dt.DataTable(id='my_datatable',
                         columns=[{"name": i, "id": i} for i in df_competitor.loc[:, ['MOTHER_BRAND', 'VOLUME',
                                                                                      'TOTAL_AMT']]],
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
                         ),

        ], className='create_container2 six columns'),
        html.Div([
            dcc.Graph(
                id="piechart_1",
            ),
            dcc.Graph(
                id="piechart_2",
            ),
        ], className='create_container2 six columns')
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


@app.callback(Output('my_datatable', 'data'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')], )
def display_table(select_year, select_month):
    data_table = df_competitor[(df_competitor['YEAR'] == select_year) & df_competitor['MONTH'].isin(select_month)]
    data_table['VOLUME'] = pd.to_numeric(data_table['VOLUME'], errors='coerce')
    data_table['TOTAL_AMT'] = pd.to_numeric(data_table['TOTAL_AMT'], errors='coerce')

    data_table = data_table.groupby(by=['MOTHER_BRAND']).agg({'VOLUME': 'sum', 'TOTAL_AMT': 'sum'}).reset_index()
    data_table['VOLUME'] = data_table['VOLUME'].map('{:,.2f}'.format)
    data_table['TOTAL_AMT'] = data_table['TOTAL_AMT'].map('${:,.2f}'.format)
    data_table = data_table.sort_values("MOTHER_BRAND", ascending=True)
    return data_table.to_dict('records')


@app.callback(Output('piechart_1', 'figure'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')],
              )
def update_graph_1(select_year, select_month):
    df_competitor1 = df_competitor.copy()
    sorted_df_competitor_top_10_vol = df_competitor1[
        (df_competitor1['YEAR'] == select_year) & df_competitor1['MONTH'].isin(select_month)].sort_values("VOLUME",
                                                                                                          ascending = False)
    out_df_competitor_top_10_vol = sorted_df_competitor_top_10_vol.iloc[:11]
    out_df_competitor_top_10_vol = out_df_competitor_top_10_vol.append(
        {'MOTHER_BRAND': 'Others', 'VOLUME': sorted_df_competitor_top_10_vol['VOLUME'].iloc[11:].sum()},
        ignore_index=True,
    )

    df_graph = out_df_competitor_top_10_vol

    return px.pie(df_graph, values=df_graph['VOLUME'],
                  names=df_graph['MOTHER_BRAND'],
                  color_discrete_sequence=px.colors.sequential.Rainbow,
                  title=
                  '<b style="text-align:center;">Percent top 10 Volume in year: ' + str(select_year))


@app.callback(Output('piechart_2', 'figure'),
              [Input('select_year', 'value')],
              [Input('select_month', 'value')],
              )
def update_graph_2(select_year, select_month):
    df_competitor2 = df_competitor.copy()
    df_competitor2['TOTAL_AMT'] = pd.to_numeric(df_competitor['TOTAL_AMT'], errors='coerce')
    sorted_df_competitor_top_10_amt = df_competitor2[
        (df_competitor2['YEAR'] == select_year) & df_competitor2['MONTH'].isin(select_month)].sort_values("TOTAL_AMT",
                                                                                                          ascending=False)
    out_df_competitor_top_10_amt = sorted_df_competitor_top_10_amt.iloc[:11]
    out_df_competitor_top_10_amt = out_df_competitor_top_10_amt.append(
        {'MOTHER_BRAND': 'Others', 'TOTAL_AMT': sorted_df_competitor_top_10_amt['TOTAL_AMT'].iloc[11:].sum()},
        ignore_index=True,
    )
    df_graph = out_df_competitor_top_10_amt

    return px.pie(df_graph, values=df_graph['TOTAL_AMT'],
                  names=df_graph['MOTHER_BRAND'],
                  color_discrete_sequence=px.colors.sequential.Rainbow,
                  title=
                  '<b style="text-align:center;">Percent top 10 Amount in year: ' + str(select_year))

