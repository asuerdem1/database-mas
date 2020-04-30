import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

from db_mgt import getAllTables, getColumnNames, getTableDf

from server import app
from flask import session


def getLayout():
    years = session.get('years') if session.get('years') else [0]
    layout = html.Div([
        dcc.Location(id='out_page_url', refresh=True),
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        # html.H4(session.get('year'))
                    ]),
                    dbc.Col([
                        dbc.Button("Go Back", id="go_back")
                    ], className="text-right")
                ], className="mb-4"),

                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id='crossfilter-xaxis-column',
                            # options=[{'label': i, 'value': i} for i in getOptions()],
                            value='resources'
                        ),
                        dcc.RadioItems(
                            id='crossfilter-xaxis-type',
                            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                            value='Linear',
                            labelStyle={'display': 'inline-block'}
                        )
                    ],
                        style={'width': '48%', 'display': 'inline-block'}),

                    html.Div([
                        dcc.Dropdown(
                            id='crossfilter-yaxis-column',
                            # options=[{'label': i, 'value': i} for i in getOptions()],
                            value='sort'
                        ),
                        dcc.RadioItems(
                            id='crossfilter-yaxis-type',
                            options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                            value='Linear',
                            labelStyle={'display': 'inline-block'}
                        )
                    ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
                ]),

                html.Div([
                    dcc.Graph(
                        id='crossfilter-indicator-scatter',
                        hoverData={'points': [{'customdata': 'BE'}]}
                    )
                ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
                html.Div([
                    dcc.Graph(id='x-time-series'),
                    dcc.Graph(id='y-time-series'),
                ], style={'display': 'inline-block', 'width': '49%'}),

                html.Div(dcc.Slider(
                    id='crossfilter-year--slider',
                    min=years[0],
                    max=years[-1],
                    value=years[-1],
                    marks={str(year): str(year) for year in years},
                    step=None
                ))
            ])
        ]),
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

    # datas = session.get('datas') if session.get('datas') else []

    return [item['nick_name'] for item in datas if item['nick_name'] not in ['country']]


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
    [Input('crossfilter-xaxis-column', 'value'),
     Input('crossfilter-yaxis-column', 'value'),
     Input('crossfilter-xaxis-type', 'value'),
     Input('crossfilter-yaxis-type', 'value'), Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type, year_value):
    all_data = session.get('all_data')
    for item in all_data:
        if item['year'] == year_value:

            datas = item['datas']
            year = item['year']
            table_name = item['table_name']
            dff = getTableDf(datas, year, table_name)
            traces = []
            for i in dff.continent.unique():
                df_by_continent = dff[dff['continent'] == i]
                traces.append(dict(
                    x=df_by_continent[df_by_continent['Indicator Name'] == xaxis_column_name]['Value'],
                    y=df_by_continent[df_by_continent['Indicator Name'] == yaxis_column_name]['Value'],
                    text=df_by_continent[df_by_continent['Indicator Name'] == yaxis_column_name]['Country Name'],
                    customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
                    mode='markers',
                    marker={
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ))

            return {
                'data': traces,
                'layout': dict(
                    xaxis={
                        'title': xaxis_column_name,
                        'type': 'linear' if xaxis_type == 'Linear' else 'log'
                    },
                    yaxis={
                        'title': yaxis_column_name,
                        'type': 'linear' if yaxis_type == 'Linear' else 'log'
                    },
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }


def create_time_series(dff, axis_type, title):
    return {
        'data': [dict(
            x=dff['Year'],
            y=dff['Value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
            }],
            'yaxis': {'type': 'linear' if axis_type == 'Linear' else 'log'},
            'xaxis': {'showgrid': False}
        }
    }


@app.callback(
    Output('x-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'hoverData'),
     Input('crossfilter-xaxis-column', 'value'),
     Input('crossfilter-xaxis-type', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    all_data = session.get('all_data')
    df = None
    country_name = hoverData['points'][0]['customdata']

    for item in all_data:
        datas = item['datas']
        year = item['year']
        table_name = item['table_name']
        dfin = getTableDf(datas, year, table_name)
        dff = dfin.loc[dfin['Country Name'] == country_name]
        dff = dff.loc[dfin['Indicator Name'] == xaxis_column_name]

        if df is None:
            df = dff
        else:
            df = df.append(dff)

    return create_time_series(df, axis_type, country_name)


@app.callback(
    Output('y-time-series', 'figure'),
    [Input('crossfilter-indicator-scatter', 'hoverData'),
     Input('crossfilter-yaxis-column', 'value'),
     Input('crossfilter-yaxis-type', 'value')])
def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    all_data = session.get('all_data')
    df = None
    country_name = hoverData['points'][0]['customdata']

    for item in all_data:
        datas = item['datas']
        year = item['year']
        table_name = item['table_name']
        dfinx = getTableDf(datas, year, table_name)
        country_name = hoverData['points'][0]['customdata']
        dff = dfinx.loc[dfinx['Country Name'] == country_name]
        dff = dff.loc[dfinx['Indicator Name'] == yaxis_column_name]

        if df is None:
            df = dff
        else:
            df = df.append(dff)

    return create_time_series(df, axis_type, country_name)
