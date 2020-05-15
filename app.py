import dash
import datetime
import dash_html_components as html
import dash_core_components as dcc
import requests
import time
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go


#we initiate the application

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets = external_stylesheets)

server = app.server

# Get data on only confirmed cases
api_response = requests.get('https://covid19api.herokuapp.com/confirmed')

from pandas.io.json import json_normalize
df = json_normalize(api_response.json()['locations'][35])
BC = json_normalize(api_response.json()['locations'][36])
#manitoba
Man = json_normalize(api_response.json()['locations'][38])
Nova = json_normalize(api_response.json()['locations'][41])
ON=json_normalize(api_response.json()['locations'][42])
QB = json_normalize(api_response.json()['locations'][44])
SK = json_normalize(api_response.json()['locations'][45])

test_data = pd.read_csv('https://raw.githubusercontent.com/ishaberry/Covid19Canada/master/cases.csv')
test_data['date_report'] = pd.to_datetime(test_data['date_report'], dayfirst=True)


new_table = test_data.groupby(['date_report', 'province'], as_index=False).count()
new_table['month'] = new_table['date_report'].dt.month_name()
new_table['month number'] = new_table['date_report'].dt.month
new_table['Acc'] = new_table.groupby('province')['case_id'].cumsum()
prov = ['Repatriated', 'PEI']
new_table = new_table[~new_table['province'].isin(prov)]
final = new_table.groupby(['province','month','month number'], as_index=False)['case_id'].sum().sort_values(by=['month number'])
test_table_week = new_table.groupby(['province', pd.Grouper(key='date_report', freq='W-SUN')])['case_id'].sum().reset_index().sort_values('date_report').rename(columns={'case_id':'Total cases per week'})
test_table_ave = new_table.groupby(['province', pd.Grouper(key='date_report', freq='W-SUN')])['case_id'].mean().reset_index().sort_values('date_report').rename(columns={'case_id':'Ave cases per week'}).round()
final_test_ave_sum = pd.merge(test_table_week, test_table_ave, on=['date_report', 'province'], how='left')
final_test_ave_sum['week_number'] = final_test_ave_sum['date_report'].dt.week

print(new_table)

"""
def clean(table):

    df = table.transpose()
    df = df.reset_index(level=0)
    #first rows are location only so we removed them

    df1 = df.loc[6:, :]
    df1.rename(columns={0: "values"}, inplace=True)
    #convert data to numeric and date type
    df1.loc[:,'values'] = pd.to_numeric(df1['values'])
    #we clean the date column
    df1['index'] = df1['index'].str.split('.').str[-1]
    df1['index'] = pd.to_datetime(df1['index'])

    #sort values
    df1.sort_values(by=['index'], inplace=True)

    #amount per month

    df1['month'] = df1['index'].dt.month_name()

    return df1

Alberta = clean(df)
BC_1 = clean(BC)
NS = clean(Nova)
Ontario = clean(ON)
Quebec = clean(QB)
Sask = clean(SK)
Manitoba = clean(Man)


list_prov = dict(Alberta=Alberta,BC=BC_1, NS=NS, Ontario=Ontario,Quebec=Quebec,Saskatchewan=Sask, Manitoba=Manitoba)
"""
app.layout = html.Div(id="wrapper", style={"margin-left": 'auto',"margin-right": 'auto', "width":"100%" },children=[
    html.H1('Covid Data for Canada', style={"text-align": "center", 'backgroundColor': '#1a2d46', 'color': '#ffffff', 'padding-bottom': '0%'}),
    dcc.Tabs([
        dcc.Tab(label='Daily cases per province', style={'text-shadow': '2px 2px 5px grey', 'font-size': 20}, children=[
            html.Div(className='row', style={'columnCount': 2},children=[
                html.Div(children=[
                    html.H6("""Select a province""", className='col s12 m6', style={'width': '50%'}),
                    html.A("Edgar Lizarraga Linkedin profile", href='https://www.linkedin.com/in/edgar-lizarraga/', target='_blank', style={ "display": "block", "text-align": "right",'padding-top': '20px'}),
                ]),

            ]),

            dcc.Dropdown(
                id='input',
                style=dict(width='40%', verticalAlign='middle'),
                options=[({'label': i, 'value': i}) for i in new_table['province'].unique()],
                placeholder='Select province',
                multi=False
            ),

            dcc.Loading(loading_state=dict(is_loading=True) ,
                        children=[
                html.Div(className='row', style={'display': 'flex', 'margin-left': '1%', 'margin-right': '1%'}, children=[
                    html.H4(id='second-result', className= 'col s12 m6',
                            style={'backgroundColor': '#0075af', 'color': 'white', 'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',"box-shadow": '10px 10px 5px grey','width': '30%', 'display': 'online-block', 'text-align': 'center'}),
                    html.H4(id='third', className='col s12 m6',
                            style={'backgroundColor': '#9b9b69', 'color': 'white', 'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',"box-shadow": '10px 10px 5px grey','width': '30%', 'display': 'online-block', 'text-align': 'center'}),
                    html.H4(id='fourth', className='col s12 m6',
                            style={'backgroundColor': '#a77e55', 'color': 'white', 'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',"box-shadow": '10px 10px 5px grey','width': '30%', 'display': 'online-block', 'text-align': 'center'}),


                ])
            ], type='graph', fullscreen=False),

            dcc.Interval(
                id='interval-component',
                interval=2000*1000,
                n_intervals=0
            ),
            dcc.Loading(children=[
                html.Div(className='row',children=[

                    dcc.Graph(id='slider-graph', animate=True,style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40,'padding-top': '1%', 'padding-bottom': '0%','height': 500}),
                    dcc.Graph(id='testtest', animate=True, style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40, 'height': 500}),

                ]),
            ]),

        ]),
        dcc.Tab(label='Weekly average', style={'text-shadow': '2px 2px 5px grey', 'font-size': 20}, children=[
            html.H6("""Select a province""", style={'margin-right': '2em'}),
                dcc.Dropdown(
                        id='input_3',
                        style=dict(width='40%', verticalAlign='middle'),
                        options=[({'label': i, 'value': i}) for i in new_table['province'].unique()],
                        placeholder='Select province',
                        multi=False
                ),
                dcc.Loading(loading_state=dict(is_loading=True) ,
                        children=[
                            html.Div(className='test3', style={'display': 'flex', 'margin-left': '5%', "box-shadow": '10px 10px 5px grey'}, children=[
                                html.H4(id='third-tap-result', className= 'col s12 m6',
                                     style={'backgroundColor': '#0075af', 'color': 'white', 'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',"box-shadow": '10px 10px 5px grey','width': '30%', 'display': 'online-block', 'text-align': 'center'}),
                                html.H4(id='third-tap-result_2', className='col s12 m6',
                                    style={'backgroundColor': '#9b9b69', 'color': 'white', 'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',"box-shadow": '10px 10px 5px grey','width': '30%', 'display': 'online-block', 'text-align': 'center'}),
                                html.H4(id='third-tap-result_3', className='col s12 m6',
                                    style={'backgroundColor': '#a77e55', 'color': 'white', 'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',"box-shadow": '10px 10px 5px grey','width': '30%', 'display': 'online-block', 'text-align': 'center'}),

                            ])
                ], type='default', fullscreen=False),
                dcc.Interval(
                    id='interval_for_weekly_graph',
                    interval=2000*1000,
                    n_intervals=0
                ),
                dcc.Loading(children=[
                    html.Div(className='test3', children=[
                        dcc.Graph(id='slider-graph-third', animate=True,style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40, 'padding-top': '1%','height': 500})
                    ])
                ], type='graph'),


        ])
    ], style=dict(backgroundColor='black')),


])


@app.callback(
    [Output(component_id='slider-graph', component_property='figure'),Output('second-result', 'children'), Output('third', 'children'), Output('fourth', 'children')],
    [Input(component_id='input', component_property='value'), Input('interval-component', 'n_intervals')]
)
def update(value, n_intervals):
    print(value)
    print(n_intervals)


    if value:

        time.sleep(2)
        x = new_table[new_table['province']==value]['date_report']
        y = new_table[new_table['province']==value]['case_id']

        ave_value = [y.mean()] * len(y)
        theshhold = 1.0


        graph = go.Scatter(
            x=x,
            y=y,
            name= 'Daily values',
            mode='lines',
            line=dict(shape='spline',
                      smoothing=1.3,
                      color='blue'),
            fill='tozeroy'
        )

        trace = go.Scatter(
            x=x,
            y=ave_value,
            name='Ave',
            line=dict(width=3,
                      color='red'),
        )

        data = [graph, trace]

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            xaxis = dict(range=[min(x), max(x)]),
            yaxis = dict(range=[min(y), max(y)]),
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
            title='Daily cases'
        )

        return {'data': data, 'layout': layout}, f'{value} Latest report: {x.iloc[-1].month_name()} {x.iloc[-1].day}', f'New cases: {y.iloc[-1]}', f'Totals: {y.sum():,}'

    if value is None or n_intervals:
        print('lets see')
        time.sleep(2)

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
        )
        return {'data': [
            ({'x': new_table[new_table['province']==i]['date_report'], 'y': new_table[new_table['province']==i]['case_id'], 'name': i,'type':'scatter', 'mode':'lines', "fill":'tozeroy','line': {'shape': 'spline', 'smoothing':1.3}}) for i in new_table['province'].unique()
        ],'layout': layout}, "","",""

@app.callback(
    Output('testtest', 'figure'),
    [Input('input', 'value'), Input('interval-component', 'n_intervals')]
)
def update_second_tap(value2, n_interval):
    print(f"this is the second chart {value2}")

    if value2:


        """set x value"""
        x = new_table[new_table['province']==value2]['date_report']
        y = new_table[new_table['province']==value2]['Acc']



        tap2_grapgh = go.Scatter(
            x=x,
            y=y,
            name='Acc Values',
            mode='lines',
            line=dict(shape='spline',
                      smoothing=1.3,
                      color='blue'),
            fill='tozeroy'
        )
        data= [tap2_grapgh]

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            xaxis=dict(range=[min(x), max(x) + datetime.timedelta(days=7)]),
            yaxis=dict(range=[min(y), max(y)]),
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
            title='Acc totals'
        )

        return {'data': data,'layout': layout}

    elif value2 is None or n_interval:

        time.sleep(2)

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f')
        )

        return {'data': [(
            {'x': new_table[new_table['province']==x]['date_report'], 'y': new_table[new_table['province']==x]['Acc'], 'name': x, "fill":'tozeroy'}) for x in new_table['province'].unique()], 'layout': layout}

@app.callback(
    [Output('slider-graph-third', 'figure'), Output('third-tap-result', 'children'), Output('third-tap-result_2', 'children'), Output('third-tap-result_3', 'children')],
    [Input('input_3', 'value'), Input('interval_for_weekly_graph', 'n_intervals')]
)
def weekly(value3, n_intervals):
    print(final_test_ave_sum.dtypes)

    x = final_test_ave_sum[final_test_ave_sum['province'] == value3]['date_report']
    x2 = final_test_ave_sum[final_test_ave_sum['province'] == value3]['Total cases per week']
    y = final_test_ave_sum[final_test_ave_sum['province'] == value3]['Ave cases per week']

    if value3:

        time.sleep(2)

        print(y)

        graph_third_tap = go.Scatter(
            x=x,
            y=y,
            yaxis='y1',
            name='Daily values',
            line=dict(width=3,
                      color='red'),
            mode='markers',
            marker=dict(
                color='red',
                size=7),
            fill = 'tozeroy'
        )

        second = go.Bar(
            x=x,
            y=x2,
            yaxis='y2'
        )
        data=[graph_third_tap]

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            xaxis=dict(range=[min(x), max(x) + datetime.timedelta(days=7)],
                       title='Weeks'),
            yaxis=dict(range=[min(y), max(y)+30],
                       title='Ave per week',
                       showline=True),
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f')
        )

        return {'data': data, 'layout': layout}, f'Beginning of week on day {x.iloc[-2].day}', f"Previous week totals: {int(y.iloc[-2])}", f'Current week totals: {int(y.iloc[-1])}'
    elif value3 is None or n_intervals:

        print(f'third {value3} and {n_intervals}')
        time.sleep(2)

        layout = go.Layout(
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

        return {'data': [
            {'x': final_test_ave_sum[final_test_ave_sum['province']==j]['date_report'], 'y': final_test_ave_sum[final_test_ave_sum['province']==j]['Ave cases per week'], "name":j, "fill":'tozeroy'} for j in final_test_ave_sum['province'].unique()
        ], 'layout': layout}, "","", ""

if __name__=="__main__":
    app.run_server(debug=True)