import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
from flask import session

from db_mgt import getTableDf
from server import app
import pandas as pd


def get_layout():
    years = session.get('years') if session.get('years') else [0]
    i_options = np.array(['country', 'gender', 'age', 'rel_area'])
    v_options = np.array(['animals', 'env', 'faith', 'health', 'resources', 'sort'])

    layout = html.Div([
        html.Div([
            html.Div([
                html.Label('Measurement Indicators'),
                dcc.Dropdown(
                    id='v-dropdown',
                    options=[{'label': i, 'value': i} for i in v_options],
                    value='health'
                ),
                dcc.Dropdown(
                    id='v2-dropdown',
                    options=[{'label': i, 'value': i} for i in v_options],
                    value='resources'
                ),
            ],
                style={'width': '49%', 'display': 'inline-block'}),

            html.Div([
                html.Label('Categorical Indicators'),
                dcc.Dropdown(
                    id='i-dropdown',
                    options=[{'label': i, 'value': i} for i in i_options],
                    value='gender'
                ),
                dcc.Dropdown(
                    id='i2-dropdown',
                    options=[{'label': i, 'value': i} for i in i_options],
                    value='age'
                ),

            ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
        ], style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '10px 5px'
        }),

        html.Div([
            dcc.Graph(
                id='crossfilter-map',
                clickData={'points': [{'hovertext': 'BEL'}]}
            ),
            dcc.Graph(id='contour-plot'),
        ], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'}),

        html.Div([
            dcc.Graph(id='vio-plot'),
            dcc.Graph(id='par-plot'),
            dcc.Graph(id='area-plot'),

        ], style={'display': 'inline-block', 'width': '49%'}),

        dcc.Slider(
            id='year--slider',
            min=years[0],
            max=years[-1],
            value=years[-1],
            marks={str(year): str(year) for year in years},
            step=None
        )

    ])

    return layout


@app.callback(
    Output('crossfilter-map', 'figure'),
    [Input('v-dropdown', 'value'), Input('year--slider', 'value')])
def update_map_graph(var, year_value=2010):
    all_data = session.get('all_data')

    for item in all_data:
        if item['year'] == year_value:
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[1]
            hovertext = dff['country']
            fig = go.Figure(data=go.Choropleth(
                locations=dff['country'],
                z=dff[var],
                # text = dff['country'],
                hovertext=dff['country'],
                colorscale='Blues',
                autocolorscale=False,
                reversescale=True,
                marker_line_color='darkgray',
                marker_line_width=0.5,
                # colorbar_tickprefix = '$',
                colorbar_title='Indicator',
            ))

            fig.update_layout(
                title_text='Title',
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    projection_type='equirectangular'
                ),
                annotations=[dict(
                    x=0.55,
                    y=0.1,
                    xref='paper',
                    yref='paper',
                    text='More Info: <a href="https://www.cia.gov/library/publications/resources/the-world-factbook/index.html">\
                    CIA World Factbook</a>',
                    showarrow=False
                )]
            )
            fig.update_geos(lataxis_range=[30, 70], lonaxis_range=[-25, 35])
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            return fig


@app.callback(
    Output('vio-plot', 'figure'),
    [Input('crossfilter-map', 'clickData'), Input('i-dropdown', 'value'), Input('i2-dropdown', 'value'),
     Input('v-dropdown', 'value'), Input('year--slider', 'value')])
def update_vio(clickData, ind, ind2, var, year_value):
    all_data = session.get('all_data')

    for item in all_data:
        if item['year'] == year_value:
            country_name = clickData['points'][0]['hovertext']
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[2]
            dff = dff[dff['country'] == country_name].dropna()
            fig = px.violin(dff, x=dff[ind], y=dff[var], color=dff[ind2], box=True, violinmode='overlay', hover_data=dff.columns)
            xx = dff.groupby(ind).agg(['mean', 'median', 'std', 'skew', pd.Series.kurt])[var]
            li = xx.columns.tolist()
            v = np.round(xx.values, 2)
            v = np.append(li, v)
            v = np.array_split(v, len(xx) + 1)
            lst = xx.index.tolist()
            lst[0:0] = ['stat']

            trace = go.Table(
                columnwidth=[80, 160],
                header=dict(values=lst),
                cells=dict(values=v),
                domain=dict(x=[0, 1],
                            y=[0, 0.3])
            )

            fig.update_xaxes(title_text='')
            fig.update_layout(dict(xaxis1=dict(dict(domain=[0.15, 1], anchor='y1')),
                                   yaxis1=dict(dict(domain=[0.4, 1], anchor='x1'))))
            title = '<b>{}</b><br>{}'.format(country_name, var)
            fig.update_layout(title_text=title)
            fig.add_trace(trace)
            return fig


@app.callback(
    Output('par-plot', 'figure'),
    [Input('crossfilter-map', 'clickData'), Input('i-dropdown', 'value'), Input('i2-dropdown', 'value'),
     Input('v-dropdown', 'value'), Input('year--slider', 'value')])
def update_par(clickData, ind, ind2, var, year_value):
    all_data = session.get('all_data')

    for item in all_data:
        if item['year'] == year_value:
            country_name = clickData['points'][0]['hovertext']
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[2]
            dff = dff[dff['country'] == country_name].dropna()
            # df = dff[[ind, ind2, var]]
            fig = px.parallel_categories(dff, dimensions=[ind, ind2, var], color=var)
            return fig


@app.callback(
    Output('area-plot', 'figure'),
    [Input('crossfilter-map', 'clickData'), Input('i-dropdown', 'value'), Input('i2-dropdown', 'value'),
     Input('v-dropdown', 'value'), Input('year--slider', 'value')])
def update_are(clickData, ind, ind2, var, year_value):
    all_data = session.get('all_data')

    for item in all_data:
        if item['year'] == year_value:
            country_name = clickData['points'][0]['hovertext']
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[2]
            dff = dff[dff['country'] == country_name].dropna()
            fig = px.area(dff, x=ind, y=var, color=ind2)
            fig['layout']['yaxis1'].update(title='', range=[0, 10], autorange=False)
            return fig


@app.callback(
    Output('contour-plot', 'figure'),
    [Input('crossfilter-map', 'clickData'), Input('v-dropdown', 'value'), Input('v2-dropdown', 'value'),
     Input('year--slider', 'value')])
def update_con(clickData, v1, v2, year_value):
    all_data = session.get('all_data')

    for item in all_data:
        if item['year'] == year_value:
            country_name = clickData['points'][0]['hovertext']
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[2]
            dff = dff[dff['country'] == country_name].dropna()
            fig = px.scatter(dff, x=v1, y=v2, trendline="ols", marginal_y="histogram", marginal_x="histogram")
            trace2 = go.Histogram2dContour(
                x=dff[v1], y=dff[v2], name='density', ncontours=20,
                colorscale='Hot', reversescale=True, showscale=False, hoverinfo='skip'
            )
            fig.add_trace(trace2)
            return fig
