import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import os
import webbrowser
from dash.exceptions import PreventUpdate
import cmd_kill
import socket #for port detection $Multi-user
import time
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
df = pd.read_csv("data annotation demo nrg.csv")
df = df[['SEQ_NUM', 'Estimated Class','Probability','NAME', 'COMPANY_NAME','HELPTEXT']]
input_file_len = len(df)
 # final df =
app.layout = html.Div(
             [
            html.Br(),
            html.Br(),
            html.Div(
            [
                dash_table.DataTable(
                    css=[{
                        'selector': '.dash-spreadsheet td div',
                        'rule': '''
                                line-height: 15px;
                                max-height: 30px; min-height: 30px; height: 30px;
                                display: block;
                                overflow-y: hidden;
                            '''
                    }],
                    id='datatable-interactivity',
                    columns=[
                        {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
                    ],
                    data=df.to_dict('records'),
                    editable=True,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    column_selectable="single",
                    row_selectable="multi",
                    row_deletable=True,
                    selected_columns=[],
                    selected_rows=[],
                    page_action='none',
                    style_table={'height': '500px', 'overflowY': 'auto'},
                    style_cell_conditional=[
                            {'if': {'column_id': 'SEQ_NUM'},
                             'width': '5%'},
                            {'if': {'column_id': 'Estimated Class'},
                             'width': '5%'},
                            {'if': {'column_id': 'Probability'},
                             'width': '7%'},
                            {'if': {'column_id': 'NAME'},
                             'width': '10%'},
                            {'if': {'column_id': 'COMPANY_NAME'},
                             'width': '10%'},
                    ],
                    style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                    style_header={'backgroundColor': '#36476c', 'fontWeight': 'bold', 'color': 'white' },
                    style_cell={
                        'backgroundColor': 'rgb(240,240,240)',
                        'color': '#36476c',
                        'textAlign': 'left',
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 0,
                    },
                        tooltip_data=[
                                                {
                                                    column: {'value': str(value), 'type': 'markdown'}
                                                    for column, value in row.items()
                                                } for row in df.to_dict('rows')
                                            ],
                                            tooltip_duration=None
                )
            ]),
            html.Div(
            children = [
            html.Button('Select All', id='button3', n_clicks_timestamp = 0,
                        style = {
                          'background-color': '#36476c',
                          'color': 'white',
                            'border': '2px solid white',
                            'padding': 10}),
            html.Button('Annotate', id='button', n_clicks_timestamp = 0,
                        style = {
                          'background-color': '#36476c',
                          'color': 'white',
                          'border': '2px solid white',
                        'padding': 10}),
            ],style={'textAlign': 'center',}
        ),
        html.Div([html.Div(id = 'output-1', children ='')],style={'textAlign': 'center'}),
        html.Div([html.Div(id = 'target', children ='')],style={'textAlign': 'center'}),
            ]
        )
# Callback for the 'Annotate' button
@app.callback(
    Output('output-1', 'children'),
    [Input('button', 'n_clicks')],
    [State('datatable-interactivity', 'derived_virtual_data'),
    State('datatable-interactivity', 'derived_virtual_selected_rows')])
def run_script_onClick_annotate(n_clicks, rows, derived_virtual_selected_rows):
    # Don't run unless the button has been pressed...
    if not n_clicks:
        raise PreventUpdate
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    else:
        selected_rows = [rows[i] for i in derived_virtual_selected_rows]
        df = pd.DataFrame(selected_rows)
    df = df.replace('\n', '', regex=True)
    df1 = df['HELPTEXT']
    df1.to_csv(r'data.txt', header=None, index=None, sep=' ', mode='w')
    # a temporary text file to contain the data that is to be streamed to prodigy
    fh = open('data.txt', "r")
    # run the ner.correct command to annotate the records
    system_cmd = 'python -m prodigy textcat.manual trial_dataset2 data.txt --loader txt --label YES,NO --exclusive'
    os.system(system_cmd)
    return ''
# Callback for embedding the prodigy page when 'Annotate' button is hit
@app.callback(
    [Output('datatable-interactivity','selected_rows'), Output('target', 'children')],
    [ Input('button3', 'n_clicks_timestamp'), Input('button', 'n_clicks_timestamp')], [State('datatable-interactivity', "selected_rows")])
def run_script_onClick_embed(n_clicks1, n_clicks2, selected_rows):
#     # Don't run unless the button has been pressed...
    if n_clicks1 < 0 and n_clicks2 < 0:
        raise PreventUpdate
    if int(n_clicks1) <= int(n_clicks2):
        cmd_kill.kill()
        time.sleep(2)
        while socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(('localhost', 8080)) != 0:
            time.sleep(3)
            pass
        # current_time = str(int(round(time.time() * 1000)))
        return [], html.Iframe(src='http://localhost:8080/?s=' + str(n_clicks2), width=1000, height=600) # Iframe layout to embed prodigy
    else:
        # print(current_time)
        # try:
        if n_clicks2 > 0:
            return [i for i in range(input_file_len)], html.Iframe(src='http://localhost:8080/?s=' + str(n_clicks2), width=1000, height=600)
        else:
            return [i for i in range(input_file_len)], ''
# run the server
if __name__ == '__main__':
    app.run_server()