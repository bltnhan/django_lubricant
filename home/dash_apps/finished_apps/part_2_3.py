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
df_group_2_3 = df.groupby(by=['CLASSIFICATION','INDUSTRY','YEAR','MONTH']).agg({'VOLUME':'sum','TOTAL_AMT':'sum'}).reset_index()
df_group_2_3['TOTAL_AMT'] = df_group_2_3['TOTAL_AMT'].map('${:,.2f}'.format)
df_group_2_3['CLASSIFICATION'].unique()