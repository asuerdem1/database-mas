import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

from db_mgt import getAllTables, getColumnNames

from server import app
from flask import session


def getLayout():
    se_year = str(session.get('year')) if session.get('year') else ""
    layout = html.Div([
        dcc.Location(id='in_page_url', refresh=True),
        dbc.Row([
            dbc.Col([
                html.Span("Don't forget to assign year to the data!", className="text-secondary")
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Select Data", html_for="table_dropdown"),
                    dcc.Dropdown(
                        id="table_dropdown",
                        options=[{'label': i, 'value': i} for i in getAllTables()]
                    )
                ])
            ]),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label("Add Year:"),
                            dbc.Input(
                                type="number",
                                id="year_val"
                            )
                        ])
                    ])
                ])
            ]),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label("*", className="text-danger"),
                            dbc.Button("Add Year", color="primary", id="add_year", className="w-100 mb-3")
                        ], className="justify-content-end")
                    ])
                ])
            ]),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Select country", html_for="country_dropdown"),
                    dcc.Dropdown(id="country_dropdown")
                ])
            ]),
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Select continent", html_for="continent_dropdown"),
                    dcc.Dropdown(id="continent_dropdown")
                ])
            ]),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Select sex", html_for="sex_dropdown"),
                    dcc.Dropdown(id="sex_dropdown")
                ])
            ]),
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Select age", html_for="age_dropdown"),
                    dcc.Dropdown(id="age_dropdown")
                ])
            ]),
        ]),

        dbc.Row([
            dbc.Col([
                html.Span("Always start with assigning the country variable first, enter min max only for numerical variables!", className="text-secondary")
            ])
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Select a variable", html_for="variable_dropdown"),
                    dcc.Dropdown(
                        id="variable_dropdown",
                    )
                ])
            ]),
            dbc.Col([
                dbc.FormGroup([
                    dbc.Label("Rename:", id="var_rename", html_for="rename_var"),
                    dbc.Input(
                        type="text",
                        id="rename_var",
                        placeholder="Enter New Name"
                    )
                ]),
            ]),
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label("Min", html_for="var_min"),
                            dbc.Input(
                                type="text",
                                id="var_min",
                            )
                        ])
                    ]),
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label("Max", html_for="var_max"),
                            dbc.Input(
                                type="text",
                                id="var_max",
                            )
                        ])
                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Add", color="primary", id="add_button", className="w-100 mb-3")
                    ])
                ]),
            ])

        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label(id="error-msg", className="text-danger"),
                dbc.Label(id="error-msg1", className="text-danger")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.H5("Table Name: " + session.get('table_name') if session.get('table_name') else "", id="show_table_name")
            ]),
            dbc.Col([
                html.H5("Year:" + se_year, id="show_year")
            ]),
        ]),

        # Suat ekleme 1 başlangıç

        dbc.Row([
            dbc.Col([
                dbc.Button("Clear Session", id="clear_btn", color="secondary")
            ], className="text-right mt-4")
        ]),

        # Suat ekleme 1 bitiş

        dbc.Row([
            dbc.Col(drawShowData(), id="show-data")
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Button("Scatter", id="scatter-button", color="primary")
            ], className="text-right mt-4")
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Button("Map", id="map-button", color="primary")
            ], className="text-right mt-4")
        ]),

        html.Div(id='invisible', style={'visibility': 'hidden'})
    ])
    return layout


@app.callback(
    [
        Output('variable_dropdown', 'options'),
        Output('country_dropdown', 'options'),
        Output('continent_dropdown', 'options'),
        Output('country_dropdown', 'value'),
        Output('continent_dropdown', 'value'),
        Output('show_table_name', 'children'),
        Output('sex_dropdown', 'options'),
        Output('age_dropdown', 'options'),
    ],
    [Input('table_dropdown', 'value')])
def logout_dashboard(table_name):
    if table_name:
        session['table_name'] = table_name
        session['year'] = None
        variables = [{'label': i['name'], 'value': i['name']} for i in getColumnNames(table_name)]
        return variables, variables, variables, "", "", "Table Name: " + table_name, variables, variables
    return [], "Table Name: None"


@app.callback([Output('rename_var', 'value'), Output('var_min', 'value'), Output('var_max', 'value'), Output('var_rename', 'children')],
              [Input('variable_dropdown', 'value')])
def clearVars(val_name):
    return "", "", "", "Rename: " + val_name


@app.callback([Output('show-data', 'children'), Output('variable_dropdown', 'value')], [Input('add_button', 'n_clicks')],
              [State('table_dropdown', 'value'), State('variable_dropdown', 'value'), State('rename_var', 'value'), State('var_min', 'value'), State('var_max', 'value')])
def addData(n_clicks, table, variable, nick_name, min_v, max_v):
    if n_clicks:
        if table is None or variable is None or nick_name is None:
            return drawShowData(), ""
        if session.get('year') is None or session.get('year') == "":
            return "Don't forget to add  year for the data!", ""

        all_data = session.get('all_data')
        for index, item in enumerate(all_data):
            if item['year'] == session.get("year"):
                datas = item['datas'] if item['datas'] else []
                data = {'variable': variable, 'nick_name': nick_name, 'min': min_v, 'max': max_v}
                datas.append(data)
                item['datas'] = datas
                all_data[index] = item
        session['all_data'] = all_data
    return drawShowData(), ""


@app.callback(
    Output('country_dropdown', 'children'),
    [Input('country_dropdown', 'value')],
    [State('table_dropdown', 'value')]
)
def on_country_selected(country_variable_name, table_name):
    all_data = session.get('all_data')

    if country_variable_name:
        if all_data and len(all_data) > 0:
            for data in all_data:
                if data['table_name'] == table_name:
                    data['datas'].append({
                        'nick_name': 'country',
                        'variable': country_variable_name
                    })
                    session['all_data'] = all_data
                    break

    return ""


@app.callback(
    Output('continent_dropdown', 'children'),
    [Input('continent_dropdown', 'value')],
    [State('table_dropdown', 'value')]
)
def on_continent_selected(continent_variable_name, table_name):
    all_data = session.get('all_data')

    if continent_variable_name:
        if all_data and len(all_data) > 0:
            for data in all_data:
                if data['table_name'] == table_name:
                    data['datas'].append({
                        'nick_name': 'continent',
                        'variable': continent_variable_name
                    })
                    session['all_data'] = all_data
                    break

    return ""


@app.callback(
    Output('sex_dropdown', 'children'),
    [Input('sex_dropdown', 'value')],
    [State('table_dropdown', 'value')]
)
def on_sex_selected(sex_variable_name, table_name):
    all_data = session.get('all_data')

    if sex_variable_name:
        if all_data and len(all_data) > 0:
            for data in all_data:
                if data['table_name'] == table_name:
                    data['datas'].append({
                        'nick_name': 'sex',
                        'variable': sex_variable_name
                    })
                    session['all_data'] = all_data
                    break

    return ""


@app.callback(
    Output('age_dropdown', 'children'),
    [Input('age_dropdown', 'value')],
    [State('table_dropdown', 'value')]
)
def on_age_selected(age_variable_name, table_name):
    all_data = session.get('all_data')

    if all_data and len(all_data) > 0:
        for data in all_data:
            if data['table_name'] == table_name:
                data['datas'].append({
                    'nick_name': 'age',
                    'variable': age_variable_name
                })
                session['all_data'] = all_data
                break

    return ""


@app.callback(
    Output('remove_button', 'children'),
    [Input('remove_button', 'n_clicks'),
     Input('remove_button', 'key'),
     Input('remove_button', 'className')]
)
def on_remove_button_clicked(n_clicks, row_data, year):
    if n_clicks:
        all_data = session.get('all_data') if session.get('all_data') else []
        for index_all_data in range(len(all_data)):
            if all_data[index_all_data]['year'] == year:
                for index in range(len(all_data[index_all_data]['datas'])):
                    if all_data[index_all_data]['datas'][index]['nick_name'] == row_data['nick_name']:
                        del all_data[index_all_data]['datas'][index]
                        session['all_data'] = all_data
                        return "Please click f5 to refresh"
    return "X"


def drawShowData():
    def getYear(year, table):
        year_data = dbc.Row([
            dbc.Col([
                html.H5("{} : {}".format(table, year), className="text-success")
            ])
        ])
        return year_data

    def getRow(row_data, year_d):
        row = dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Label(row_data['variable'])
                    ]),
                    dbc.Col([
                        dbc.Label('=')
                    ]),
                    dbc.Col([
                        dbc.Label(row_data['nick_name'])
                    ])
                ])], width=6),
            dbc.Col([
                dbc.Label('Min Value: ' + (row_data.get('min') or ''))
            ]),
            dbc.Col([
                dbc.Label('Max Value: ' + (row_data.get('max') or ''))
            ]),
            dbc.Button(children=[dbc.Label('X')], key=row_data, className=year_d, id='remove_button'),
        ])
        return row

    # session.clear()
    all_data = session.get('all_data') if session.get('all_data') else []
    table_data = []
    for data in all_data:
        y_data = getYear(data['year'], data['table_name'])
        data_year = data['year']
        if y_data:
            table_data.append(y_data)
        for item in data['datas']:
            table_data.append(getRow(item, data_year))

    return table_data if table_data != [] else ""


# suat ekleme 2 başlangıç
@app.callback(Output('clear_btn', 'children'), [Input('clear_btn', 'n_clicks')])
def clear(n_clicks):
    if n_clicks:
        session.clear()
        dcc.Location(pathname="/", id="someid_doesnt_matter")
        return "CLEAR SESSION (Please click f5 to refresh)"
    return "Clear Session"


# suat ekleme 2 bitiş

@app.callback(Output('show_year', 'children'), [Input('add_year', 'n_clicks')], [State('year_val', 'value'), State('table_dropdown', 'value')])
def setYear(n_clicks, year, table):
    if n_clicks:
        if session.get("table_name") is None:
            return "Year: Don't forget to select the data"
        if year == "" or year is None:
            return "Year: Please type a year"
        session['year'] = year
        setYearsList(year)
        years = {'year': year, 'datas': [], 'table_name': table}
        all_data = session.get('all_data') if session.get('all_data') else []
        # all_data.append(years)
        flag = False
        for index, item in enumerate(all_data):
            if item['year'] == year:
                flag = True
        if not flag:
            all_data.append(years)
        session['all_data'] = all_data
    return "Year: {}".format(session.get('year') if session.get('year') else "")


@app.callback(
    [Output('url', 'pathname'),
     Output('error-msg', 'children')],
    [Input('scatter-button', 'n_clicks'),
     Input('map-button', 'n_clicks')]
)
def go_to_graphs_output_page(is_scatter_button_clicked, is_map_button_clicked):
    if session.get('year') is None or session.get('year') == "":
        return None, "Year is Not Found!"
    elif is_scatter_button_clicked:
        return '/output-scatter', None
    elif is_map_button_clicked:
        return '/output-map', None
    return None, ""


def setYearsList(year):
    s_years = session.get('years') if session.get('years') else []
    if not int(year) in s_years:
        s_years.append(int(year))
        s_years.sort()
        session['years'] = s_years
