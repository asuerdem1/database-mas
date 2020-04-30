import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

from db_mgt import  getAllTables, getColumnNames

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
                        ], className="justify-contetn-end")
                    ])
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
                        # options=[{'label': i, 'value': i} for i in getAllTables()]
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
                        dbc.Button("Rename", color="primary", id="add_button", className="w-100 mb-3")
                    ])
                ]),
            ])

        ]),
        dbc.Row([
            dbc.Col([
                dbc.Label(id="error-msg", className="text-danger")
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
        dbc.Row([
            dbc.Col(drawShowData(), id="show-data")
        ]),
        dbc.Row([
            dbc.Col([
                # dbc.Button("Clear", id="session_clear", color="danger", className="mr-3"),
                dbc.Button("Submit", id="submit_btn", color="primary")

            ],className="text-right mt-4")
        ])
    ])

    return layout

# @app.callback([Output])

@app.callback([Output('variable_dropdown', 'options'), Output('show_table_name', 'children')],
              [Input('table_dropdown', 'value')])
def logout_dashboard(table_name):
    if table_name:
        session['table_name'] = table_name
        session['year'] = None
        return [{'label': i['name'], 'value': i['name']} for i in getColumnNames(table_name)], "Table Name: " + table_name
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

        alldata = session.get('alldata')
        for index, item in enumerate(alldata):
            if item['year'] == session.get("year"):
                datas = item['datas'] if item['datas'] else []
                data = {'variable': variable, 'nick_name': nick_name, 'min': min_v, 'max': max_v}
                datas.append(data)
                item['datas'] = datas
                alldata[index] = item
        session['alldata'] = alldata
    return drawShowData(), ""

def drawShowData():

    def getYear(year, table):
        year_data = dbc.Row([
            dbc.Col([
                html.H5("{} : {}".format(table, year), className="text-success")
            ])
        ])
        return year_data
    def getRow(data):
        row = dbc.Row([
            dbc.Col([dbc.Row([
                dbc.Col([
                    dbc.Label("Variables: ")
                ]),
                dbc.Col([
                    dbc.Label(data['variable'])
                ]),
                dbc.Col([
                    dbc.Label('=')
                ]),
                dbc.Col([
                    dbc.Label(data['nick_name'])
                ])
            ])], width=6),
            dbc.Col([
                dbc.Label('Min Value: ' + data['min'])
            ]),
            dbc.Col([
                dbc.Label('Max Value: ' + data['max'])
            ]),
        ])
        return row

    # try:
    alldata = session.get('alldata') if session.get('alldata') else []
    table_data = []
    for data in alldata:
        y_data = getYear(data['year'], data['table_name'])
        if y_data != []:
            table_data.append(y_data)
        for item in data['datas']:
            table_data.append(getRow(item))

    return table_data if table_data != [] else ""
    # except:
    #     return ""

@app.callback(Output('show_year', 'children'), [Input('add_year', 'n_clicks')], [State('year_val', 'value'), State('table_dropdown', 'value')])
def setYear(n_clicks, year, table):
    if n_clicks:
        if session.get("table_name") is None:
            return "Year: Don't forget to select the data"
        if year == "" or year == None:
            return "Year: Please type a year"
        session['year'] = year
        setYearsList(year)
        years = {'year': year, 'datas': [], 'table_name': table}
        alldata = session.get('alldata') if session.get('alldata') else []
        # alldata.append(years)
        flag = False
        for index, item in enumerate(alldata):
            if item['year'] == year:
                flag = True
        if not flag:
            alldata.append(years)
        session['alldata'] = alldata
    return "Year: {}".format(session.get('year') if session.get('year') else "")

@app.callback([Output('in_page_url', 'pathname'), Output('error-msg', 'children')], [Input('submit_btn', 'n_clicks')])
def submit(n_clicks):
    if n_clicks:
        if session.get('year') is None or session.get('year') == "":
            return None, "Year is Not Found!"
        return '/output', None
    return None, ""

def setYearsList(year):
    s_years = session.get('years') if session.get('years') else []
    if not int(year) in s_years:
        s_years.append(int(year))
        s_years.sort()
        session['years'] = s_years
