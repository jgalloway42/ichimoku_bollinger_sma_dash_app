# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 17:16:23 2022

@author: jfell
"""
from StockAnalysisFunctions2 import *
import pandas_datareader.data as web
import dash
from dash import html,dcc
from dash.dependencies import Input,Output,State
import pandas as pd

'''Define Constants and setup notebook'''
# Stock Market Source (https://finance.yahoo.com/)
stocks = list(pd.read_csv('dashboard_stocks.csv').columns)
stocks_var = len(stocks)*['Close']
stock_desc = list(pd.read_csv('dashboard_descs.csv'))
stock_source = 'yahoo'


# Time Frame Variables
startDate = dt.datetime.now() - dt.timedelta(weeks=78)
adj_startDate = startDate - dt.timedelta(days=400)
endDate = dt.datetime.now()
recentDate = dt.datetime.now() - dt.timedelta(weeks=52)
ytDate = dt.datetime(dt.datetime.now().year,1,1)

# init stock funcitons
sfa = SFA()

# Convenience Constants
TICKER, SOURCE, VAR, DESC, DATA = 0,1,2,3,4  # Constants for Dictionary List entry


''' Combine all ticker labels in to one master list'''

master_list = []
for row in [[stocks, stock_source, stocks_var, stock_desc]]:
    # source loop
    for i,tick in enumerate(row[0]):
        master_list.append([tick,row[SOURCE],row[VAR][i],row[DESC][i]])

#collect all data in dictionary
master_dict = {}
for i in range(len(master_list)):
    tick,src,var,desc = master_list[i]
    print(tick, desc)
    df = web.DataReader(tick,src,adj_startDate,endDate)
    df = df.astype(np.float16, errors='ignore')
    df = df.dropna(axis=0,how='all')
    master_dict[tick] = [tick,src,var,desc,df]


# add moving averages to stocks from yahoo
for i,key in enumerate(master_dict.keys()):
    if master_dict[key][SOURCE] == stock_source:
        master_dict[key][DATA] = sfa.add_moving_avgs(master_dict[key][DATA])   


# add ichi and bb to stocks from yahoo
for i,key in enumerate(master_dict.keys()):
    if master_dict[key][SOURCE] == stock_source:
        master_dict[key][DATA] = sfa.add_cumulative_return(master_dict[key][DATA])
        master_dict[key][DATA] = sfa.add_bollinger_bands(master_dict[key][DATA])
        master_dict[key][DATA] = sfa.add_ichimoku(master_dict[key][DATA])

# crop data to selected time frames
for i,key in enumerate(master_dict.keys()):
    if master_dict[key][SOURCE] == stock_source:
        master_dict[key][DATA] = master_dict[key][DATA].loc[
            master_dict[key][DATA].index >= startDate]

'''Create App'''
app = dash.Dash()

# setup simple layout
app.layout = html.Div(children=[
    html.H1(children='Stock Price Dashboard',style={'text-align':'center'}),
    dcc.Dropdown(id='picker-dropdown',
                 options=stocks,
                 value=stocks[0],
                 style={'width':'40%'}),
    dcc.Graph(id='ichimoku-graph'),
    dcc.Graph(id='bollinger-graph'),
    dcc.Graph(id='moving-average-graph')
    
])

@app.callback(
    [Output(component_id='ichimoku-graph',component_property='figure'),
    Output(component_id='bollinger-graph',component_property='figure'),
    Output(component_id='moving-average-graph',component_property='figure')],
    [Input(component_id='picker-dropdown',component_property='value')]
)

def update_graph(selected_symbol):
    f_ichi = sfa.plot_ichimoku(master_dict[selected_symbol][DATA],
                              master_dict[selected_symbol][DESC])
    f_bol = sfa.plot_with_boll_bands(master_dict[selected_symbol][DATA],
                              master_dict[selected_symbol][DESC])
    f_ma = sfa.plot_with_ma(master_dict[selected_symbol][DATA],
                              master_dict[selected_symbol][DESC])
    
    return f_ichi,f_bol,f_ma


# run local server
if __name__ == '__main__':
    app.run_server(debug=True)











