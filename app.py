#!/bin/python3
# For Windows run below file first
# venv\Scripts\activate.bat

# For mac/Linux run below file first
# venv\Scripts\activate

import base64
import datetime
import io
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
df = []

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    
])


def parse_contents(contents, filename, date):
    global df
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

        options = []
        for col in df.columns:
            options.append({'label':'{}'.format(col, col), 'value':col})
        # print("options", options) 


    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        html.Label("Select a feature from drop-down to plot on X Axis"),
	    dcc.Dropdown(
	        id = 'my_dropdown1',
	        options = options
	    ),
	    html.Label("Select a feature from drop-down to plot on Y Axis"),
	    dcc.Dropdown(
	        id = 'my_dropdown2',
	        options = options
	    ),
	    html.Label(id='my_label1'),
	    html.Button(
	        id='submit-button',
	        n_clicks=0,
	        children='Submit',
	        style={'fontSize':24, 'marginLeft':'30px'}
	    ),

		dcc.Graph(
			id='graph',
			figure=px.scatter(df, x="Volume", y="Volume") 
		),


        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ])


@app.callback(Output('output-data-upload', 'children'),[
              Input('upload-data', 'contents')],[
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


def create_figure():

    layout = dict(xaxis=dict(range=[0, 7], showgrid=False), yaxis=dict(range=[0, 3.5]), showlegend=False,
             shapes=[dict(type='rect', x0=1, y0=1, x1=2, y1=3, line=dict(color='RoyalBlue'))])
    data = go.Scatter(x=[1.5], y=[0.75])
    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(
    Output('graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_dropdown1','value'), State('my_dropdown2','value')]
    )

def update_figure(selected_value, value1 = "Volume", value2 = "Volume"):
    global df
    print("value1, value2, df", value1, value2)
    
    x = df[value1].to_list()
    y = df[value2].to_list()

    # print("x", x)

    return px.scatter(df, x=value1, y=value2) 
    return px.Scatter(x=x, y=y)

    return {
                "data": [
                    {
                        "x": x,
                        "y": y,
                        "type": "scatter",
                    },
                ],
                "layout": {"title": "Plot"},
            }
    # return go.Scatter(x=x, y=y)


if __name__ == '__main__':
    app.run_server(debug=False)