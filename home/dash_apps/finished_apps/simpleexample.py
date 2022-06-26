import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import dash_table as dt
import dash_bootstrap_components as dbc
import pathlib


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('SimpleExample', external_stylesheets=external_stylesheets)
app.css.append_css({ "external_url" : "/static/css/s1.css" })

#app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

PATH = pathlib.Path(__file__).parent # lấy thư mục chứa file python
DATA_PATH = PATH.joinpath("./data").resolve() # nối với

data = pd.read_csv(DATA_PATH.joinpath('raw_data.csv'))

year_list = list(data['Nam'].unique()) # lấy ra list năm để bỏ vào slider

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H5('CASE STUDY 1 DASHBOARD | DASH PLOTLY', className = 'title_text'),
            ])
        ], className = "title_container twelve columns")
    ], className = "row flex-display"),

    html.Div([
        html.Div([
            html.Div([
             html.P('CHỌN KHU VỰC:'),
             html.P('CHỌN QUỐC GIA:'),
                     ], className = 'adjust_title'),
          html.Div([
            dcc.Dropdown(id = 'select_continent',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         value = 'Asia',
                         placeholder = 'CHỌN KHU VỰC',
                         options = [{'label': c, 'value': c}
                                    for c in data['Khu_Vuc'].unique()]),


            dcc.Dropdown(id = 'select_countries',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         placeholder = 'CHỌN QUỐC GIA',
                         options = []),
              ], className = 'adjust_drop_down_lists'),

            html.P('CHỌN NĂM:', className = 'fix_label', style = {'color': 'black'}),
            dcc.RangeSlider(id = 'select_years',
                            min = year_list[0],
                            max = year_list[-1],
                            step = None,
                            updatemode='drag',
                            value = [year_list[3], year_list[-2]],
                            marks = {str(yr): str(yr) for yr in year_list}
                            ),

        ], className = "create_container2 six columns", style = {'margin-bottom': '10px', "margin-top": "10px"}),

        html.Div([
         html.Div([
            html.Div(id = 'text1'),
            html.Div(id = 'text2'),
            html.Div(id = 'text3'),
                ], className = 'adjust_inline')
        ], className = "create_container2 six columns", style = {'margin-bottom': '10px', "margin-top": "10px"}),

    ], className = "row flex-display"),

    html.Div([
        html.Div([
            dcc.RadioItems(id = 'radio_items',
                           labelStyle = {"display": "inline-block"},
                           options = [{'label': 'TUỔI THỌ', 'value': 'life_expectancy'},
                                      {'label': 'DÂN SỐ', 'value': 'population'},
                                      {'label': 'GDP BÌNH QUÂN', 'value': 'gdp_Per_cap'}],
                           value = 'life_expectancy',
                           style = {'text-align': 'center', 'color': 'black'},
                           className = 'dcc_compon'),
            dcc.Graph(id = 'line_chart',
                      config = {'displayModeBar': 'hover'}),

        ], className = 'create_container2 six columns'),

        html.Div([
            dt.DataTable(id = 'my_datatable',
                         columns = [{'name': i, 'id': i} for i in
                                    data.loc[:, ['Quoc_Gia', 'Nam', 'Dan_So',
                                                 'Khu_Vuc', 'Tuoi_Tho', 'GDP_Binh_Quan']]],
                         sort_action = "native",
                         style_table = {"overflowX": "auto"},
                         sort_mode = "multi",
                         virtualization = True,
                         style_cell = {'textAlign': 'left',
                                       'min-width': '100px',
                                       'backgroundColor': '#F2F2F2',
                                       },
                         style_as_list_view = False,
                         style_header = {
                             'backgroundColor': '#16a085',
                             'fontWeight': 'bold',
                             'font': 'Times New Roman',
                             'color': 'white',
                             'border': '1px solid #9A38D5'
                         },
                         style_data = {'textOverflow': 'hidden', 'color': 'black',
                                       'border': '1px solid orange'},
                         fixed_rows = {'headers': True},
                         )

        ], className = 'create_container2 six columns'),

    ], className = "row flex-display"),

], id= "mainContainer", style={"display": "flex", "flex-direction": "column"})

@app.callback(
    Output('select_countries', 'options'),
    Input('select_continent', 'value')) # nhap chau luc ra nuoc
def get_country_options(select_continent):
    data1 = data[data['Khu_Vuc'] == select_continent]
    return [{'label': i, 'value': i} for i in data1['Quoc_Gia'].unique()]



@app.callback(
    Output('select_countries', 'value'),
    Input('select_countries', 'options'))
# @app.callback(
 #   Output(component_id='my-output', component_property='children'),
 #   Input(component_id='my-input', component_property='value')


def get_country_value(select_countries):
    return [k['value'] for k in select_countries][0]


@app.callback(Output('text1', 'children'),
              [Input('select_continent', 'value')],
              [Input('select_years', 'value')])

def update_text(select_continent, select_years):
    data1 = data.groupby(['Quoc_Gia', 'Nam', 'Khu_Vuc'])[['Dan_So', 'Tuoi_Tho', 'GDP_Binh_Quan']].sum().reset_index()
    data2 = data1[(data1['Khu_Vuc'] == select_continent) & (data1['Nam'] >= select_years[0]) & (data1['Nam'] <= select_years[1])].nlargest(1, columns = ['Dan_So'])
    data_continent = data2['Khu_Vuc'].iloc[0]
    top_year = data2['Nam'].iloc[0]
    top_country = data2['Quoc_Gia'].iloc[0]
    top_pop = data2['Dan_So'].iloc[0]

    return [

               html.H6(f'QUỐC GIA ĐỨNG ĐẦU VỀ DÂN SỐ Ở KHU VỰC: {data_continent.upper()}',
                       style = {'textAlign': 'center',
                                'line-height': '1',
                                'color': '#c0392b'}
                       ),
               html.P(f'NĂM: {top_year}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-3px'
                               }
                      ),
               html.P(f'ĐẤT NƯỚC: {top_country.upper()}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-10px'
                               }
                      ),
               html.P(f'DÂN SỐ: {top_pop:,.0f}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-10px'
                               }
                      ),


    ]

@app.callback(Output('text2', 'children'),
              [Input('select_continent', 'value')],
              [Input('select_years', 'value')])

def update_text(select_continent, select_years):
    data1 = data.groupby(['Quoc_Gia', 'Nam', 'Khu_Vuc'])[['Dan_So', 'Tuoi_Tho', 'GDP_Binh_Quan']].sum().reset_index()
    data2 = data1[(data1['Khu_Vuc'] == select_continent) & (data1['Nam'] >= select_years[0]) & (data1['Nam'] <= select_years[1])].nlargest(1, columns = ['Tuoi_Tho'])
    data_continent = data2['Khu_Vuc'].iloc[0]
    top_year = data2['Nam'].iloc[0]
    top_country = data2['Quoc_Gia'].iloc[0]
    top_lifeexp = data2['Tuoi_Tho'].iloc[0]

    return [

               html.H6(f'QUỐC GIA ĐỨNG ĐẦU VỀ TUỔI THỌ Ở KHU VỰC: {data_continent.upper()}',
                       style = {'textAlign': 'center',
                                'line-height': '1',
                                'color': '#c0392b'}
                       ),
               html.P(f'NĂM: {top_year}',
                      style = {'textAlign': 'center',
                               'color': 'black',
                               'fontSize': 15,
                               'margin-top': '-3px'
                               }
                      ),
               html.P(f'ĐẤT NƯỚC: {top_country.upper()}',
                      style = {'textAlign': 'center',
                               'color': 'black',
                               'fontSize': 15,
                               'margin-top': '-10px'
                               }
                      ),
               html.P(f'TUỔI THỌ: {top_lifeexp:,.0f}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-10px'
                               }
                      ),


    ]

@app.callback(Output('text3', 'children'),
              [Input('select_continent', 'value')],
              [Input('select_years', 'value')])

def update_text(select_continent, select_years):
    data1 = data.groupby(['Quoc_Gia', 'Nam', 'Khu_Vuc'])[['Dan_So', 'Tuoi_Tho', 'GDP_Binh_Quan']].sum().reset_index()
    data2 = data1[(data1['Khu_Vuc'] == select_continent) & (data1['Nam'] >= select_years[0]) & (data1['Nam'] <= select_years[1])].nlargest(1, columns = ['GDP_Binh_Quan'])
    data_continent = data2['Khu_Vuc'].iloc[0]
    top_year = data2['Nam'].iloc[0]
    top_country = data2['Quoc_Gia'].iloc[0]
    top_gdppercap = data2['GDP_Binh_Quan'].iloc[0]

    return [

               html.H6(f'QUỐC GIA ĐỨNG ĐẦU VỀ GDP Ở KHU VỰC: {data_continent.upper()}',
                       style = {'textAlign': 'center',
                                'line-height': '1',
                                'color': '#c0392b'}
                       ),
               html.P(f'NĂM: {top_year}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-3px'
                               }
                      ),
               html.P(f'QUỐC GIA: {top_country.upper()}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-10px'
                               }
                      ),
               html.P(f'GDP BÌNH QUÂN: {top_gdppercap:,.0f}',
                      style = {'textAlign': 'center',
                               'fontSize': 15,
                               'margin-top': '-10px'
                               }
                      ),
    ]



@app.callback(Output('line_chart', 'figure'),
              [Input('select_continent', 'value')],
              [Input('select_countries', 'value')],
              [Input('select_years', 'value')],
              [Input('radio_items', 'value')])

def update_graph(select_continent, select_countries, select_years, radio_items):
    data1 = data.groupby(['Quoc_Gia', 'Nam', 'Khu_Vuc'])[['Dan_So', 'Tuoi_Tho', 'GDP_Binh_Quan']].sum().reset_index()
    data2 = data1[(
            data1['Khu_Vuc'] == select_continent)
             & (data1['Quoc_Gia'] == select_countries) &
                (data1['Nam'] >= select_years[0])
                & (data1['Nam'] <= select_years[1])]

    if radio_items == 'life_expectancy':

     return {
        'data':[
            go.Scatter(
                x = data2['Nam'],
                y = data2['Tuoi_Tho'],
                mode = 'text + markers + lines',
                text = data2['Tuoi_Tho'],
                texttemplate = '%{text:.0f}',
                textposition = 'bottom right',
                line = dict(width = 3, color = '#38D56F'),
                marker = dict(size = 10, symbol = 'circle', color = '#38D56F',
                              line = dict(color = '#38D56F', width = 2)
                              ),
                textfont = dict(
                    family = "Times New Roman",
                    size = 12,
                    color = 'black'),

                hoverinfo = 'text',
                hovertext =
                '<b>QUỐC GIA</b>: ' + data2['Quoc_Gia'].astype(str) + '<br>' +
                '<b>NĂM</b>: ' + data2['Nam'].astype(str) + '<br>' +
                '<b>KHU VỰC</b>: ' + data2['Khu_Vuc'].astype(str) + '<br>' +
                '<b>TUỔI THỌ</b>: ' + [f'{x:,.3f}' for x in data2['Tuoi_Tho']] + '<br>'

            )],


        'layout': go.Layout(
             plot_bgcolor='#ecf0f1',
             paper_bgcolor='#ecf0f1',
             title={
                'text': '<b>TUỔI THỌ TỪ' + ' ' + ' ĐẾN '.join([str(y) for y in select_years]),

                'y': 0.99,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
             titlefont={
                        'color': '#38D56F',
                        'size': 17},

             hovermode='closest',
             margin = dict(t = 15, r = 0),

             xaxis = dict(title = '<b>NĂM</b>',
                          visible = True,
                          color = 'black',
                          showline = True,
                          showgrid = False,
                          showticklabels = True,
                          linecolor = 'black',
                          linewidth = 1,
                          ticks = 'outside'
                         ),

             yaxis = dict(title = '<b>TUỔI THỌ</b>',
                          visible = True,
                          color = 'black',
                          showline = False,
                          showgrid = True,
                          showticklabels = True,
                          linecolor = 'black',
                          linewidth = 1,
                          ticks = ''
                         ),

            legend = {
                'orientation': 'h',
                'bgcolor': '#1f2c56',
                'x': 0.5,
                'y': 1.25,
                'xanchor': 'center',
                'yanchor': 'top'},

            font = dict(
                family = "Times New Roman",
                size = 12,
                color = 'white'),

        )

    }

    elif radio_items == 'population':

     return {
        'data':[
            go.Scatter(
                x = data2['Nam'],
                y = data2['Dan_So'],
                mode = 'text + markers + lines',
                text = data2['Dan_So'],
                texttemplate = '%{text:,.2s}',
                textposition = 'top center',
                line = dict(width = 3, color = '#9A38D5'),
                marker = dict(size = 10, symbol = 'circle', color = '#9A38D5',
                              line = dict(color = '#9A38D5', width = 2)
                              ),
                textfont = dict(
                    family = "Times New Roman",
                    size = 12,
                    color = 'black'),

                hoverinfo = 'text',
                hovertext =
                '<b>QUỐC GIA</b>: ' + data2['Quoc_Gia'].astype(str) + '<br>' +
                '<b>NĂM</b>: ' + data2['Nam'].astype(str) + '<br>' +
                '<b>KHU VỰC</b>: ' + data2['Khu_Vuc'].astype(str) + '<br>' +
                '<b>DÂN SỐ</b>: ' + [f'{x:,.0f}' for x in data2['Dan_So']] + '<br>'

            )],


        'layout': go.Layout(
             plot_bgcolor='#ecf0f1',
             paper_bgcolor='#ecf0f1',
             title={
                'text': '<b>DÂN SỐ TỪ' + ' ' + ' ĐẾN '.join([str(y) for y in select_years]),

                'y': 0.99,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
             titlefont={
                        'color': '#9A38D5',
                        'size': 17},

             hovermode='closest',
             margin = dict(t = 15, r = 0),

             xaxis = dict(title = '<b>NĂM</b>',
                          visible = True,
                          color = 'black',
                          showline = True,
                          showgrid = False,
                          showticklabels = True,
                          linecolor = 'black',
                          linewidth = 1,
                          ticks = 'outside'
                         ),

             yaxis = dict(title = '<b>DÂN SỐ</b>',
                          visible = True,
                          color = 'black',
                          showline = False,
                          showgrid = True,
                          showticklabels = True,
                          linecolor = 'black',
                          linewidth = 1,
                          ticks = ''
                         ),

            legend = {
                'orientation': 'h',
                'bgcolor': '#1f2c56',
                'x': 0.5,
                'y': 1.25,
                'xanchor': 'center',
                'yanchor': 'top'},

            font = dict(
                family = "Times New Roman",
                size = 12,
                color = 'white'),

        )

    }

    elif radio_items == 'gdp_Per_cap':

     return {
        'data':[
            go.Scatter(
                x = data2['Nam'],
                y = data2['GDP_Binh_Quan'],
                mode = 'text + markers + lines',
                text = data2['GDP_Binh_Quan'],
                texttemplate = '%{text:,.0f}',
                textposition = 'bottom right',
                line = dict(width = 3, color = '#FFA07A'),
                marker = dict(size = 10, symbol = 'circle', color = '#FFA07A',
                              line = dict(color = '#FFA07A', width = 2)
                              ),
                textfont = dict(
                    family = "Times New Roman",
                    size = 12,
                    color = 'black'),

                hoverinfo = 'text',
                hovertext =
                '<b>QUỐC GIA</b>: ' + data2['Quoc_Gia'].astype(str) + '<br>' +
                '<b>NĂM</b>: ' + data2['Nam'].astype(str) + '<br>' +
                '<b>KHU VỰC</b>: ' + data2['Khu_Vuc'].astype(str) + '<br>' +
                '<b>GDB BÌNH QUÂN</b>: ' + [f'{x:,.6f}' for x in data2['GDP_Binh_Quan']] + '<br>'

            )],


        'layout': go.Layout(
             plot_bgcolor='#ecf0f1',
             paper_bgcolor='#ecf0f1',
             title={
                #'text': '<b>GDB BÌNH QUÂN TỪ' + ' ' + ' ĐẾN '.join([str(y) for y in select_years]),
                'text': '<b>GDB BÌNH QUÂN TỪ' + str(select_years[0]) + ' ĐẾN ' + str(select_years[1]),
                'y': 0.99,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
             titlefont={
                        'color': '#e67e22',
                        'size': 15},

             hovermode='closest',
             margin = dict(t = 15, r = 0),

             xaxis = dict(title = '<b>NĂM</b>',
                          visible = True,
                          color = 'black',
                          showline = True,
                          showgrid = False,
                          showticklabels = True,
                          linecolor = 'black',
                          linewidth = 1,
                          ticks = 'outside'
                         ),

             yaxis = dict(title = '<b>GDP BÌNH QUÂN</b>',
                          visible = True,
                          color = 'black',
                          showline = False,
                          showgrid = True,
                          showticklabels = True,
                          linecolor = 'black',
                          linewidth = 1,
                          ticks = ''
                         ),

            legend = {
                'orientation': 'h',
                'bgcolor': '#1f2c56',
                'x': 0.5,
                'y': 1.25,
                'xanchor': 'center',
                'yanchor': 'top'},

            font = dict(
                family = "Times New Roman",
                size = 12,
                color = 'white'),

        )

    }

@app.callback(Output('my_datatable', 'data'),
              [Input('select_continent', 'value')],
              [Input('select_countries', 'value')],
              [Input('select_years', 'value')])
def display_table(select_continent, select_countries, select_years):
    data_table = data[(data['Khu_Vuc'] == select_continent) & (data['Quoc_Gia'] == select_countries) &
                      (data['Nam'] >= select_years[0]) & (data['Nam'] <= select_years[1])]
    return data_table.to_dict('records')

#
# app.layout = html.Div([
#     html.H1('Square Root Slider Graph'),
#     dcc.Graph(id='slider-graph', animate=True, style={"backgroundColor": "#1a2d46", 'color': '#ffffff'}),
#     dcc.Slider(
#         id='slider-updatemode',
#         marks={i: '{}'.format(i) for i in range(20)},
#         max=20,
#         value=2,
#         step=1,
#         updatemode='drag',
#     ),
# ])
#
#
# @app.callback(
#                Output('slider-graph', 'figure'),
#               [Input('slider-updatemode', 'value')])
# def display_value(value):
#
#
#     x = []
#     for i in range(value):
#         x.append(i)
#
#     y = []
#     for i in range(value):
#         y.append(i*i)
#
#     graph = go.Scatter(
#         x=x,
#         y=y,
#         name='Manipulate Graph'
#     )
#     layout = go.Layout(
#         paper_bgcolor='#27293d',
#         plot_bgcolor='rgba(0,0,0,0)',
#         xaxis=dict(range=[min(x), max(x)]),
#         yaxis=dict(range=[min(y), max(y)]),
#         font=dict(color='white'),
#
#     )
#     return {'data': [graph], 'layout': layout}