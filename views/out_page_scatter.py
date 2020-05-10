import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import session

from db_mgt import getTableDf
from server import app

import plotly.express as px
import numpy as np
import plotly.figure_factory as ff


def getLayout():
    years = session.get('years') if session.get('years') else [0]

    layout = html.Div([
        dcc.Location(id='out_page_url', refresh=True),
        html.Div([
            html.Div([

                html.Div([
                    dcc.Dropdown(id='x-dropdown'),
                ], style={'width': '49%', 'display': 'inline-block'}),

                html.Div([
                    dcc.Dropdown(id='y-dropdown'),
                ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),

                html.Div([
                    dcc.Dropdown(
                        id='t-dropdown',
                        multi=True,
                        # value=v_options.tolist(),
                    ),
                ], style={'width': '49%', 'display': 'inline-block'}),

            ], style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'
            }),

            html.Div([
                dcc.Graph(
                    id='crossfilter-indicator-scatter',
                    clickData={'points': [{'hovertext': 'BEL'}]}
                ),
                dcc.Graph(id='cor-plot'),
            ], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'}),

            html.Div([
                dcc.Graph(id='x-time-series'),
                dcc.Graph(id='y-time-series'),
            ], style={'display': 'inline-block', 'width': '49%'}),

            html.Div(dcc.Slider(
                id='year--slider',
                min=years[0],
                max=years[-1],
                value=years[-1],
                marks={str(year): str(year) for year in years},
                step=None
            ), style={'width': '49%', 'padding': '0px 20px 20px 20px'})
        ])
    ])

    return layout


def getOptions(year=0):
    all_data = session.get('all_data') if session.get('all_data') else []
    datas = []
    if year == 0:
        year = session.get('years')[-1] if session.get('years') else 0

    for item in all_data:
        if item['year'] == year:
            datas = item['datas']

    return [item['nick_name'] for item in datas if item['nick_name'] not in ['country']]


@app.callback(
    [Output('x-dropdown', 'options'),
     Output('y-dropdown', 'options'),
     Output('t-dropdown', 'options')],
    [Input('year--slider', 'value')]
)
def get_dropdown_options(year):
    all_data = session.get('all_data')
    for item in all_data:
        if item['year'] == year:
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[3]
            options = dff.columns.to_numpy()
            i_options = np.array(['country', 'sex', 'age', 'continent', 'year'])
            v_options = np.array(list(set(options) - set(i_options)))
            dropdown_options = [{'label': i, 'value': i} for i in v_options]
            return dropdown_options, dropdown_options, dropdown_options


@app.callback(Output('out_page_url', 'pathname'), [Input('go_back', 'n_clicks')])
def goBack(n_clicks):
    if n_clicks:
        session['datas'] = []
        session['year'] = ""
        session['all_data'] = []
        session['table_name'] = ""
        session['years'] = []
        return '/'
    return None


@app.callback([Output('crossfilter-xaxis-column', 'options'), Output('crossfilter-yaxis-column', 'options')], [Input('crossfilter-year--slider', 'value')])
def updateAxiss(year):
    options = getOptions(year)
    return [{'label': i, 'value': i} for i in options], [{'label': i, 'value': i} for i in options]


@app.callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    [Input('x-dropdown', 'value'),
     Input('y-dropdown', 'value'),
     Input('year--slider', 'value')])
def update_graph(v1, v2, year_value):
    all_data = session.get('all_data')
    for item in all_data:
        if item['year'] == year_value:
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[3]
            fig = px.scatter(dff, x=v1, y=v2, color='continent', hover_name='country', marginal_y="violin",
                             marginal_x="rug", trendline="ols")
            return fig


@app.callback(
    Output('x-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'clickData'),
     Input('x-dropdown', 'value')]
)
def update_x_timeseries(clickData, v1):
    all_data = session.get('all_data')
    df = None
    country_name = clickData['points'][0]['hovertext']

    for item in all_data:
        datas = item['datas']
        year = item['year']
        table_name = item['table_name']
        dfin = getTableDf(datas, year, table_name)[3]
        dff = dfin.loc[dfin['country'] == country_name]

        if df is None:
            df = dff
        else:
            df = df.append(dff)

    country_name = clickData['points'][0]['hovertext']
    dff = df[df['country'] == country_name]
    fig = px.scatter(dff, x='year', y=v1)
    fig.data[0].update(mode='markers+lines')
    title = '<b>{}</b><br>{}'.format(country_name, v1)
    fig.update_layout(title_text=title)
    return fig


@app.callback(
    Output('y-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'clickData'),
     Input('y-dropdown', 'value')]
)
def update_y_timeseries(clickData, v1):
    all_data = session.get('all_data')
    df = None
    country_name = clickData['points'][0]['hovertext']

    for item in all_data:
        datas = item['datas']
        year = item['year']
        table_name = item['table_name']
        dfin = getTableDf(datas, year, table_name)[3]
        dff = dfin.loc[dfin['country'] == country_name]

        if df is None:
            df = dff
        else:
            df = df.append(dff)

    country_name = clickData['points'][0]['hovertext']
    dff = df[df['country'] == country_name]
    fig = px.scatter(dff, x='year', y=v1)
    fig.data[0].update(mode='markers+lines')
    title = '<b>{}</b><br>{}'.format(country_name, v1)
    fig.update_layout(title_text=title)
    return fig


@app.callback(
    Output('cor-plot', 'figure'),
    [Input('year--slider', 'value'),
     Input('t-dropdown', 'value')]
)
def update_graph(year_value, value):
    all_data = session.get('all_data')
    for item in all_data:
        if item['year'] == year_value:
            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)[3]
            dff.set_index('country', inplace=True)
            fig = ff.create_scatterplotmatrix(dff[value], diag='histogram', text=dff.index, height=800, width=800)
            return fig
