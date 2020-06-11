import dash
import datetime
from datetime import timedelta
import dash_html_components as html
import dash_core_components as dcc
import requests
import time
import pandas as pd
import numpy as np
import fbprophet
from dash.dependencies import Input, Output
import plotly.graph_objects as go


#we initiate the application

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets = external_stylesheets)

server = app.server

# Get data on only confirmed cases
api_response = requests.get('https://covid19api.herokuapp.com/confirmed')

from pandas.io.json import json_normalize

"""
df = json_normalize(api_response.json()['locations'][35])
BC = json_normalize(api_response.json()['locations'][36])
#manitoba
Man = json_normalize(api_response.json()['locations'][38])
Nova = json_normalize(api_response.json()['locations'][41])
ON=json_normalize(api_response.json()['locations'][42])
QB = json_normalize(api_response.json()['locations'][44])
SK = json_normalize(api_response.json()['locations'][45])
"""
# NEW API WITH CONFIRMED CASES PER DAY
#WE NEED THIS WITHOUT CALLING API TO GET PROPER VALUES INTO THE DROPDOWN

provinces = ['ALBERTA', 'NWT', 'YUKON', 'SASKATCHEWAN', 'ONTARIO',
       'NEW BRUNSWICK', 'NOVA SCOTIA', 'NL', 'MANITOBA',
       'BRITISH COLUMBIA', 'NUNAVUT', 'QUEBEC', 'PRINCE EDWARD ISLAND',
       'NORTHWEST TERRITORIES']


test_data = pd.read_csv('https://raw.githubusercontent.com/ishaberry/Covid19Canada/master/cases.csv')
test_data['date_report'] = pd.to_datetime(test_data['date_report'], dayfirst=True)

new_table = test_data.groupby(['date_report', 'province'], as_index=False).count()
new_table['month'] = new_table['date_report'].dt.month_name()
new_table['month number'] = new_table['date_report'].dt.month
new_table['Acc'] = new_table.groupby('province')['case_id'].cumsum()
prov = ['Repatriated', 'PEI']
new_table = new_table[~new_table['province'].isin(prov)]
final = new_table.groupby(['province', 'month', 'month number'], as_index=False)['case_id'].sum().sort_values(
    by=['month number'])
test_table_week = new_table.groupby(['province', pd.Grouper(key='date_report', freq='W-SUN')])[
    'case_id'].sum().reset_index().sort_values('date_report').rename(columns={'case_id': 'Total cases per week'})
test_table_ave = new_table.groupby(['province', pd.Grouper(key='date_report', freq='W-SUN')])[
    'case_id'].mean().reset_index().sort_values('date_report').rename(columns={'case_id': 'Ave cases per week'}).round()
final_test_ave_sum = pd.merge(test_table_week, test_table_ave, on=['date_report', 'province'], how='left')
final_test_ave_sum['week_number'] = final_test_ave_sum['date_report'].dt.week

print(new_table)


def canada(interval):
    dtt = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    dt = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')
    canada = dt[dt['location'] == 'Canada']

    dtt1 = dtt[dtt['Country/Region'] == 'Canada']

    canada['date'] = pd.to_datetime(canada['date'])
    Transpose_data = dtt1.T.reset_index(level=0).loc[4:, :]
    Transpose_data['index'] = pd.to_datetime(Transpose_data['index'])
    Transpose_data.rename(columns={36: 'values', 'index': 'date'}, inplace=True)
    Transpose_data['values'] = pd.to_numeric(Transpose_data['values'])

    trial_table = pd.merge(canada, Transpose_data, on='date', how='left')
    # calculate difference bewteen total infections vs recovered per day
    trial_table['diff'] = trial_table['total_cases'] - trial_table['values']

    return trial_table


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
app.layout = html.Div(id="wrapper", style={"margin-left": 'auto', "margin-right": 'auto', "width": "100%"}, children=[
    html.H1('Covid-19 data for Canada',
            style={"text-align": "center", 'backgroundColor': '#1a2d46', 'color': '#ffffff', 'padding-bottom': '0%'}),
    dcc.Tabs([
        dcc.Tab(label='Daily cases', style={'text-shadow': '2px 2px 5px grey', 'font-size': 20}, children=[
            html.Div(className='row', style={'columnCount': 2}, children=[
                html.Div(children=[

                    html.H6("""Select a province""", className='col s12 m6', style={"rowCount": 2,'width': '100%'}),
                    html.H6("Clear dropdown to see Canada cases", style={'font-size': "small", "font-style": "italic"}),
                    html.A([
                        html.Img(
                            src='https://cdn2.iconfinder.com/data/icons/linkedin-ui-flat/48/LinkedIn_UI-03-512.png',
                            style={'height': '10%', 'width': '10%', 'float': 'right', 'position': 'relative'}
                        )
                    ], "Check my profile", href='https://www.linkedin.com/in/edgar-lizarraga/', target='_blank'),
                ]),

            ]),

            dcc.Dropdown(
                id='input',
                style=dict(width='40%', verticalAlign='middle'),
                options=[({'label': i, 'value': i}) for i in provinces],
                placeholder='Select province',
                multi=False
            ),

            dcc.Loading(loading_state=dict(is_loading=True),
                        children=[
                            html.Div(className='row',
                                     style={'display': 'flex', 'margin-left': '1%', 'margin-right': '1%'}, children=[
                                    html.H4(id='second-result', className='col s12 m6',
                                            style={'font-size': '18px', 'backgroundColor': '#0075af', 'color': 'white',
                                                   'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                   "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                   'display': 'online-block', 'text-align': 'center'}),
                                    html.H4(id='third', className='col s12 m6',
                                            style={'font-size': '18px', 'backgroundColor': '#9b9b69', 'color': 'white',
                                                   'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                   "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                   'display': 'online-block', 'text-align': 'center'}),
                                    html.H4(id='fourth', className='col s12 m6',
                                            style={'font-size': '18px', 'backgroundColor': '#a77e55', 'color': 'white',
                                                   'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                   "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                   'display': 'online-block', 'text-align': 'center'}),
                                    html.H4(id='fifth', className='col s12 m3',
                                            style={'font-size': '18px', 'backgroundColor': '#F0E68C', 'color': 'white',
                                                   'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                   "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                   'display': 'online-block',
                                                   'text-align': 'center'}),

                                ])
                        ], type='bar', fullscreen=False),
            dcc.Loading(
                children=[
                    html.Div(className='row',id='chart-2',
                         style={'display': 'flex', 'margin-left': '2%', 'margin-right': '1%'}, children=[
                                html.H4(id='result-canada-top', className='col s12 m6', style={'font-size': '18px', 'backgroundColor': '#0075af', 'color': 'white',
                                       'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                       "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                       'display': 'online-block', 'text-align': 'center'}
                                ),
                                html.H4(id='result-canada-top2', className='col s12 m6', style={'font-size': '18px', 'backgroundColor': '#9b9b69', 'color': 'white',
                                       'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                       "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                       'display': 'online-block', 'text-align': 'center'}
                                ),
                                html.H4(id='result-canada-top3', className='col s12 m6', style={'font-size': '18px', 'backgroundColor': '#9b9b69', 'color': 'white',
                                       'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                       "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                       'display': 'online-block', 'text-align': 'center'}
                                )
                        ]
                    )
                ]),

            dcc.Interval(
                id='interval-component',
                interval=2010 * 1000,
                n_intervals=0
            ),
            dcc.Loading(children=[
                html.Div(className='row', id='charts', style={'columnCount': 1}, children=[
                    html.Div(children=[
                        html.Div(style={'columnCount': 2}, children=[
                            dcc.Graph(id='slider-graph', animate=False,
                                      style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40,
                                             'padding-top': '1%', 'padding-bottom': '0%', 'height': 500}
                                      ),
                            dcc.Graph(id='pie', style={'width': '100%'})
                        ]),


                        dcc.Graph(id='testtest', animate=False,
                                  style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40,
                                         'height': 500}
                                  ),

                    ]),

                ]),
            ], type='bar', fullscreen=False),
            dcc.Loading(children=[
                html.Div(id='canada-chart',children=[
                    dcc.Graph(id='testtest2', animate=False,
                              style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40, 'height': 500}),
                ])
            ], type='bar', fullscreen=False),

        ]),
        dcc.Tab(label='Weekly Average per Province', style={'text-shadow': '2px 2px 5px grey', 'font-size': 20}, children=[
            html.Div(className='row-1', style={'columnCount': 2}, children=[
                html.Div(children=[

                    html.H6("""Select a province""", className='col s12 m6', style={"rowCount": 2, 'width': '100%'}),
                    html.H6("Clear dropdown to see Canada cases", style={'font-size': "small", "font-style": "italic"}),
                    html.A([
                        html.Img(
                            src='https://cdn2.iconfinder.com/data/icons/linkedin-ui-flat/48/LinkedIn_UI-03-512.png',
                            style={'height': '10%', 'width': '10%', 'float': 'right', 'position': 'relative'}
                        )
                    ], href='https://www.linkedin.com/in/edgar-lizarraga/', target='_blank'),
                ]),

            ]),
            dcc.Dropdown(
                id='input_3',
                style=dict(width='40%', verticalAlign='middle'),
                options=[({'label': i, 'value': i}) for i in provinces],
                placeholder='Select province',
                multi=False
            ),
            html.Div(id='intermediate', style={'display': 'none'}),
            dcc.Loading(loading_state=dict(is_loading=True),
                        children=[
                            html.Div(className='test3',
                                     style={'display': 'flex', 'margin-left': '5%', "box-shadow": '10px 10px 5px grey'},
                                     children=[
                                         html.H4(id='third-tap-result', className='col s12 m6',
                                                 style={'font-size': '18px', 'backgroundColor': '#0075af',
                                                        'color': 'white',
                                                        'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                        "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                        'display': 'online-block', 'text-align': 'center'}),
                                         html.H4(id='third-tap-result_2', className='col s12 m6',
                                                 style={'font-size': '18px', 'backgroundColor': '#9b9b69',
                                                        'color': 'white',
                                                        'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                        "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                        'display': 'online-block', 'text-align': 'center'}),
                                         html.H4(id='third-tap-result_3', className='col s12 m6',
                                                 style={'font-size': '18px', 'backgroundColor': '#a77e55',
                                                        'color': 'white',
                                                        'text-shadow': '1px 1px 2px black, 0 0 25px blue, 0 0 5px darkblue',
                                                        "box-shadow": '10px 10px 5px grey', 'width': '30%',
                                                        'display': 'online-block', 'text-align': 'center'}),

                                     ])
                        ], type='default', fullscreen=False),
            dcc.Interval(
                id='interval_for_weekly_graph',
                interval=2000 * 1000,
                n_intervals=0
            ),
            dcc.Loading(children=[
                html.Div(className='test3', children=[
                    dcc.Graph(id='slider-graph-third', animate=False,
                              style={'backgroundColor': 'white', 'color': 'white', 'margin-bottom': 40,
                                     'padding-top': '1%', 'height': 500})
                ])
            ], type='bar'),

        ])
    ], style=dict(backgroundColor='black')),

])
@app.callback(
    Output('intermediate', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def get_data(time):
    t = time
    URL = 'https://services9.arcgis.com/pJENMVYPQqZZe20v/ArcGIS/rest/services/province_daily_totals/FeatureServer/0/query?where=1%3D1&objectIds=&time=&resultType=tile&outFields=*&returnIdsOnly=false&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=5000&sqlFormat=none&f=json&token='
    api_response = requests.get(URL)
    bc = json_normalize(api_response.json()['features'])
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate'], unit='ms')
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate'])
    clean_list = ['REPATRIATED CDN', 'CANADA', 'PEI', "REPATRIATED", 'CANADA', 'NEWFOUNDLAND AND LABRADOR']
    bc = bc[~bc['attributes.Province'].isin(clean_list)]
    bc.sort_values(by=['attributes.OBJECTID'], inplace=True)
    # still infected
    bc['attributes.DailyRecovered'] = np.where(bc['attributes.DailyRecovered'] < 0,
                                               bc['attributes.DailyRecovered'].abs(), bc['attributes.DailyRecovered'])
    bc['Total_recov'] = bc.groupby(['attributes.Province'])['attributes.DailyRecovered'].cumsum()
    bc['current'] = bc['attributes.TotalCases'] - bc['Total_recov']
    bc['attributes.Province'].replace({"BC": 'BRITISH COLUMBIA'}, inplace=True)

    return (bc.to_json(date_format='iso', orient='columns'))

@app.callback(
    [Output(component_id='slider-graph', component_property='figure'), Output('second-result', 'children'),
     Output('third', 'children'), Output('fourth', 'children'), Output('charts', 'style'), Output("fifth", 'children'), Output('canada-chart', 'style'), Output('chart-2', 'style')],
    [Input(component_id='input', component_property='value'), Input('intermediate', 'children')]
)
def update(value, json):
    print(value)
    bc = pd.read_json(json, orient='list')
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate']).dt.date
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate'])
    bc.sort_values(by=['attributes.OBJECTID'], inplace=True)

    x = bc[bc['attributes.Province'] == value]['attributes.SummaryDate']
    y = bc[bc['attributes.Province'] == value]['attributes.DailyTotals']
    y2 = bc[bc['attributes.Province'] == value]['attributes.DailyRecovered']

    if value:
        time.sleep(1)

        ave_value = [y.mean()] * len(y)
        theshhold = 1.0

        graph = go.Scatter(
            x=x,
            y=y,
            name='Confirmed',
            mode='lines',
            line=dict(shape='spline',
                      smoothing=1.3,
                      color='#FFA07A'),
            fill='tozeroy'
        )

        trace = go.Scatter(
            x=x,
            y=ave_value,
            name='Avg. confirmed cases',
            line=dict(width=3,
                      color='red'),
        )

        trace2 = go.Scatter(
            x=x,
            y=y2,
            name='Recovered',
            line=dict(shape='spline',
                      smoothing=1.0,
                      color='#6B8E23'),
            fill='tozeroy'
        )

        data = [graph, trace, trace2]

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            xaxis=dict(range=[min(x), max(x) + datetime.timedelta(days=7)],
                       title='Days'),
            yaxis=dict(range=[min([y], default=0), max(y) + int(70)],
                       title='Cases'),
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
            title='Daily Covid-19 cases: ' + value,
            legend=dict(orientation='h',
                        yanchor='top',
                        xanchor='center',
                        y=1.1,
                        x=0.5)
        )

        return {'data': data,
                'layout': layout}, f'{value} Latest report: {x.iloc[-1].month_name()} {x.iloc[-1].day}', f'New cases: {y.iloc[-1]}', f'Total infected: {bc[bc["attributes.Province"] == value]["attributes.TotalCases"].max():,}', {
                   'display': 'block'}, f'Active: {bc[bc["attributes.Province"] == value]["current"].iloc[-1]}', {'display': 'none'}, {'display': 'none'}

    if value is None:
        print('lets see')
        time.sleep(1)

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
        )
        return {'data': [], 'layout': []}, "", "", "", {'display': 'none'}, "", {'display': 'block'}, {'display': 'flex'}


@app.callback(
    Output('testtest', 'figure'),
    [Input('input', 'value'), Input('intermediate', 'children')]
)
def update_second_tap(value2, json):
    print(f"this is the second chart {value2}")
    """we convert the data coming as json format"""
    bc = pd.read_json(json, orient='list')
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate']).dt.date

    newdata = bc[bc['attributes.Province'] == value2]
    newdata = newdata[['attributes.SummaryDate', 'attributes.TotalCases']]
    newdata.rename(columns={'attributes.SummaryDate': 'ds', 'attributes.TotalCases': 'y'}, inplace=True)
    prophet = fbprophet.Prophet(changepoint_prior_scale=0.10)
    prophet.fit(newdata)

    data_preds = prophet.make_future_dataframe(periods=15, freq='D')
    data_preds_v2 = prophet.predict(data_preds)
    print(data_preds_v2)
    x = bc[bc['attributes.Province'] == value2]['attributes.SummaryDate']
    y = bc[bc['attributes.Province'] == value2]['attributes.TotalCases']
    y2 = bc[bc['attributes.Province'] == value2]['attributes.TotalActive']
    y3 = bc[bc['attributes.Province'] == value2]['attributes.TotalDeaths']

    if value2:

        time.sleep(1)
        """set x value"""

        tap2_grapgh = go.Scatter(
            x=x,
            y=y,
            name='Cumulative cases',
            mode='lines',
            line=dict(shape='spline',
                      smoothing=1.3,
                      color='#6495ED'),
            fill='tozeroy'
        )
        pred = go.Scatter(
            x = data_preds_v2['ds'],
            y = data_preds_v2['yhat'],
            name = 'Current trend forecast'
        )

        lower_pred = go.Scatter(
            x = data_preds_v2['ds'],
            y = data_preds_v2['yhat_lower'],
            name = 'Best case forecast',
            line=dict(color='rgb(0, 13, 26)', width=2, dash='dot'),
            fillcolor='rgba(231, 234, 241,.88)',
            fill='tonexty'
        )

        upper_pred = go.Scatter(
            x=data_preds_v2['ds'],
            y=data_preds_v2['yhat_upper'],
            name='Worst case forecast',
            line = dict(color='royalblue', width=2, dash='dash'),
            fillcolor='rgba(231, 234, 241,.88)',
            fill='tonexty'
        )

        trace = go.Scatter(
            x=x,
            y=y2,
            name='Active cases',
            line=dict(shape='spline',
                      smoothing=1.0,
                      color='#3CB371'),
            fill='tozeroy'
        )

        trace1 = go.Scatter(
            x=x,
            y=y3,
            name='Cumulative deaths',
            line=dict(dash="dashdot",
                      smoothing=1.0,
                      color='#DC143C'),
            fill='tozeroy'
        )

        data = [tap2_grapgh, trace, trace1, pred, lower_pred, upper_pred]

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
            title='Covid-19 curve: ' + value2,
            xaxis=dict(range=[min(x), max(data_preds_v2['ds']) + datetime.timedelta(days=5)],
                       title='Days'),
            yaxis=dict(range=[min(y), max(data_preds_v2['yhat_upper']) + int(50)],
                       title='Cases'),
            legend=dict(orientation='h',
                        yanchor='top',
                        xanchor='center',
                        y=1,
                        x=0.5)
        )

        return {'data': data, 'layout': layout}

    elif value2 is None:

        time.sleep(1)
        df = bc

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f')
        )

        return {'data': [], 'layout': []}


@app.callback(
    Output('pie', 'figure'),
    [Input('input', 'value'), Input('intermediate', 'children')]
)
def bar(value, json):
    """convert data coming from hidden div"""

    bc = pd.read_json(json, orient='list')
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate']).dt.date

    labels = ['Total tested', 'Confirmed']
    values = [bc[bc['attributes.Province'] == value]['attributes.TotalTested'].max(),
              bc[bc['attributes.Province'] == value]['attributes.TotalCases'].max()]
    print(values)

    chart = go.Pie(
        labels=labels, values=values, hole=0.3, pull=[0, 0.2]
    )
    data = [chart]

    layout = go.Layout(
        title="Total tested",
        font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
    )

    return {"data": data, 'layout': layout}


@app.callback(
    [Output('slider-graph-third', 'figure'), Output('third-tap-result', 'children'),
     Output('third-tap-result_2', 'children'), Output('third-tap-result_3', 'children')],
    [Input('input_3', 'value'), Input('intermediate', 'children')]
)
def weekly(value3, json):

    """Convert data coming from hidden Div"""
    bc = pd.read_json(json, orient='list')
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate']).dt.date
    bc['attributes.SummaryDate'] = pd.to_datetime(bc['attributes.SummaryDate'])
    bc.sort_values(by=['attributes.OBJECTID'], inplace=True)
    mean = bc.groupby(['attributes.Province', pd.Grouper(key='attributes.SummaryDate', freq='W-SUN')])[
        'attributes.DailyTotals'].mean().reset_index().round()
    sum = bc.groupby(['attributes.Province', pd.Grouper(key='attributes.SummaryDate', freq='W-SUN')])[
        'attributes.DailyTotals'].sum().reset_index().round()
    newtable_group = pd.merge(mean, sum, on=['attributes.SummaryDate', 'attributes.Province'], how='left')
    newtable_group.rename(
        columns={'attributes.SummaryDate': 'date', 'attributes.DailyTotals_x': 'Ave', 'attributes.DailyTotals_y': 'Sum',
                 "attributes.Province": 'Province'}, inplace=True)



    x = newtable_group[newtable_group['Province'] == value3]['date']
    y = newtable_group[newtable_group['Province'] == value3]['Ave']
    y2 = newtable_group[newtable_group['Province'] == value3]['Sum']

    if value3:

        time.sleep(1)

        graph_third_tap = go.Scatter(
            x=x,
            y=y,
            yaxis='y1',
            name='Weekly average',
            line=dict(width=3,
                      color='#F4A460'),
            mode='markers',
            marker=dict(
                color='red',
                size=7),
            fill='tozeroy'
        )

        trace = go.Scatter(
            x=x,
            y=y2,
            yaxis='y1',
            name='Weekly total',
            line=dict(width=3,
                      color='#FAF0E6'),
            mode='markers',
            marker=dict(
                color='#C0C0C0',
                size=7),
            fill='tozeroy'
        )

        data = [graph_third_tap, trace]

        layout = go.Layout(
            paper_bgcolor="white",
            plot_bgcolor='white',
            xaxis=dict(range=([min(x), max(x) + datetime.timedelta(days=7)]),
                       title='Weeks'),
            yaxis=dict(range=([min(y), max(y2) + int(5)]),
                       title='Cases',
                       showline=True),
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
            title='Weekly new cases for: ' + value3
        )

        return {'data': data,
                'layout': layout}, f'Current week: {x.iloc[-2].month_name()} {(x.iloc[-2] + timedelta(1)).day} - {x.iloc[-1].month_name()} {x.iloc[-1].day} ', f"Previous week totals: {int(y.iloc[-2])}", f'Current week totals: {int(y.iloc[-1])}'
    elif value3 is None:

        print(f'third {value3} and')
        time.sleep(1)

        layout = go.Layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            yaxis=dict(title='Cases'),
            xaxis=dict(title='Weeks'),
            title="Weekly new cases",
            font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
        )

        return {'data': [
            {'x': newtable_group[newtable_group['Province'] == j]['date'],
             'y': newtable_group[newtable_group['Province'] == j]['Ave'], "name": j, "fill": 'tozeroy'} for j in
            newtable_group['Province'].unique()
        ], 'layout': layout}, "", "", ""


@app.callback(
    [Output('testtest2', 'figure'), Output('result-canada-top', 'children'), Output('result-canada-top2', 'children'), Output('result-canada-top3', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_second_tap(n_interval):
    print(f"this is the second chart {n_interval}")
    time.sleep(1)
    table = canada(n_interval)

    data_pred = table.rename(columns={'date': 'ds', "total_cases": 'y'})
    prophet = fbprophet.Prophet(changepoint_prior_scale=0.15)
    prophet.fit(data_pred)

    pred = prophet.make_future_dataframe(periods=10, freq='D')
    res = prophet.predict(pred)

    # newdata = bc[bc['attributes.Province'] == value2]
    # newdata = newdata[['attributes.SummaryDate', 'attributes.TotalCases']]
    # newdata.rename(columns={'attributes.SummaryDate': 'ds', 'attributes.TotalCases': 'y'}, inplace=True)
    # prophet = fbprophet.Prophet(changepoint_prior_scale=0.10)
    # prophet.fit(newdata)
    #
    # data_preds = prophet.make_future_dataframe(periods=15, freq='D')
    # data_preds_v2 = prophet.predict(data_preds)


    x = table['date']
    y = table['total_cases']

    tap2_grapgh = go.Scatter(
        x=x,
        y=y,
        name='Cum. cases for Canada',
        mode='lines',
        line=dict(shape='spline',
                  smoothing=1.3,
                  color='blue'),
        fill='tozeroy'
    )

    lower_pred = go.Scatter(
        x=res['ds'],
        y=res['yhat_lower'],
        name='Best case forecast',
        line=dict(color='rgb(0, 13, 26)', width=2, dash='dot')
    )

    upper_pred = go.Scatter(
        x=res['ds'],
        y=res['yhat_upper'],
        name='Worst case forecast',
        line=dict(color='royalblue', width=2, dash='dash'),
        fillcolor='rgba(231, 234, 241,.88)',
        fill='tonexty'
    )

    pred = go.Scatter(
        x=res['ds'],
        y=res['yhat'],
        name='Current trend forecast'
    )

    current = go.Scatter(
        x=x,
        y=table['diff'],
        name='Active cases',
        line=dict(shape='spline',
                  smoothing=1.3,
                  color='#FF8C00'),
        fill='tozeroy',
        hoverlabel=dict(
            bgcolor='white'
        )
    )

    deaths = go.Scatter(
        x=x,
        y=table['total_deaths'],
        name='Cum. deaths',
        line=dict(shape='spline',
                  smoothing=1.3,
                  color='red'),
        fill='tozeroy'
    )

    data = [tap2_grapgh, current, deaths, lower_pred, pred, upper_pred]

    layout = go.Layout(
        paper_bgcolor="white",
        plot_bgcolor='white',
        xaxis=dict(range=[min(x), max(res['ds']) + datetime.timedelta(days=5)],
                   title='Days'),
        yaxis=dict(range=[min(y), max(res['yhat_upper']) + int(50)],
                   title='Cases'),
        font=dict(family='Courier New monospace', size=13, color='#7f7f7f'),
        title='Covid-19 curve: Canada',
        legend=dict(orientation='h',
                    yanchor='top',
                    xanchor='center',
                    y=1,
                    x=0.5)
    )

    return {'data': data, 'layout': layout}, f'Total cases {int(table["total_cases"].max()):,}',f'Active cases: {int(table["diff"].max()):,}', f'Total deaths: {int(table["total_deaths"].max()):,}'

if __name__=="__main__":
    app.run_server(debug=True)