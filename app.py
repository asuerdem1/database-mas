# index page
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app, server
from views import in_page, out_page

from flask import session

header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%'},
        children=[
            html.Img(
                # src='assets/dash-logo-stripe.svg',
                src='assets/wise.svg',
                className='logo'
            ),
            html.Div(className='links', children=[
                html.Div(id='user-name', className='link'),
                html.Div(id='logout', className='link')
            ])
        ]
    )
)

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container'),
        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return in_page.getLayout()
    if pathname == '/output':
        return out_page.getLayout()
    return 404


if __name__ == '__main__':
    # app.run_server(host="0.0.0.0", port=int("8080"), debug=True,dev_tools_ui=True, dev_tools_props_check=True)
    app.run_server(host="0.0.0.0", port=int("8080"))
