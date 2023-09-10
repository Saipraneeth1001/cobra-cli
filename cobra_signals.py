# from nsepy import get_history
from datetime import date
import pandas as pd
import numpy as np
import talib
import datetime
import yfinance as yf
import plotly.graph_objects as go
from cobra_filter import filter_rows
from collections import defaultdict

# Fetching data from yfinance
 
def fetch_data(scrip_name):
    start_date = date(2023, 1, 1) - datetime.timedelta(300)
    return yf.Ticker(scrip_name).history(
                    start=start_date, 
                    end=date(2023,9,10))


def get_macd_indicator(row):
    last_hist = row['hist']
    prev_hist = row['prev_hist']
    indicator = 'HOLD'
    # Provide BUY or SELL indications during crossovers
    if not np.isnan(prev_hist) and not np.isnan(last_hist):
        # If hist value has changed from negative to positive or vice versa, it indicates a crossover
        macd_crossover = (abs(last_hist + prev_hist)) != (abs(last_hist) + abs(prev_hist))
        if macd_crossover:
            indicator = 'BUY' if last_hist > 0 else 'SELL'
            
    return indicator


def apply_macd_strategy(stock_df):
    stock_df['macd'],  stock_df['signal'],  stock_df['hist'] = talib.MACD(stock_df['Close'], 
                                fastperiod=12, slowperiod=26, signalperiod=9)
    stock_df['prev_hist'] = stock_df['hist'].shift(1)
    stock_df['macd_indicator'] = stock_df.apply(lambda row: get_macd_indicator(row), axis=1)
    
    return stock_df


def apply_engulfing_pattern(stock_df):
    stock_df['engulf'] = talib.CDLENGULFING(stock_df['Open'], stock_df['High'], stock_df['Low'], stock_df['Close'])
    stock_df['engulf_indicator'] = stock_df.apply(lambda row: 'BUY' if (row['engulf'] > 0) else 'SELL' if (row['engulf'] < 0) else 'HOLD', axis=1)
    return stock_df

# BUY/SELL/HOLD indicator based on the 200-days, 50-days and 20-days simple moving average
def get_ma_indicator(row):
    indicator = 'HOLD'
    row_values = [row['Close'], row['20_sma'], row['50_sma'] , row['200_sma']]
    
    # If close < 20-day sma < 50-day sma < 200-day sma --> BUY
    # If close > 20-day sma > 50-day sma > 200-day sma --> SELL
    if(row_values == sorted(row_values)):
        indicator = 'BUY'
    elif (row_values == sorted(row_values, reverse=True)):
        indicator = 'SELL'
        
    return indicator

def apply_moving_average_strategy(stock_df):
    # Compute the moving averages for 20 days, 50 days and 200 days
    stock_df['20_sma'] = stock_df['Close'].rolling(window=20).mean()
    stock_df['50_sma'] = stock_df['Close'].rolling(window=50).mean()
    stock_df['200_sma'] = stock_df['Close'].rolling(window=200).mean()

    stock_df['MA_indicator'] = stock_df.apply(lambda row: get_ma_indicator(row), axis=1)
    return stock_df

# Compute RSI
def apply_rsi_strategy(stock_df, rsi_period = 14):
    stock_df['rsi'] = talib.RSI(stock_df['Close'], rsi_period) 
    return stock_df


# Show the necessary - BUY/SELL/HOLD signals

def show_signals(scrip_name, stock):
    data = []
    count = 0
    result = []
    for index, row in stock.iterrows():
        data.append((index, row, count))
        count += 1
    for (index, row, count) in data: 
        if (row['indicator'] == 'BUY') and index.date() >= date(2023, 9, 1):
            # filter_rows(data, count)
            #print("indicator:", row['indicator'], "date:", index)
            result.append(scrip_name)
        if (row['indicator'] == 'SELL'):
            #print("indicator:", row['indicator'], "date:", index)
            pass
    
    print(result)


    

CHECK_RSI_LAST_SESSIONS = 3
RSI_LOWER_LIMIT = 40
RSI_UPPER_LIMIT = 60
def apply_trading_algo(stock_df):
    stock_df['indicator'] = 'HOLD'
    buy_sell_signals = stock_df[(stock_df['macd_indicator'] != 'HOLD') | (stock_df['MA_indicator'] != 'HOLD')| (stock_df['engulf_indicator'] != 'HOLD')]
    for index,row in buy_sell_signals.iterrows():
        # Get previous n sessions whenever a signal is reached 
        analysis_df = stock_df.loc[:index].tail(3)
        macd_ind = analysis_df.iloc[-1]['macd_indicator']
        ma_ind = analysis_df.iloc[-1]['MA_indicator']
        engulf_ind = analysis_df.iloc[-1]['engulf_indicator']
        current_indicator = 'HOLD' 
        
        # Preference given in this order: MACD, MA, engulfing pattern
        current_indicator = macd_ind if macd_ind != 'HOLD' else \
                            ma_ind if ma_ind != 'HOLD' else engulf_ind
        
        # Decide the final indicator based on the RSI value
        if ((current_indicator == 'BUY') and (analysis_df['rsi'].min() <= RSI_LOWER_LIMIT)) \
            or \
            ((current_indicator == 'SELL') and (analysis_df['rsi'].max() >= RSI_UPPER_LIMIT)): 
            stock_df.at[index, 'indicator'] = current_indicator
        
    return stock_df

# The main method to determine the signals


def my_trading_algo(scrip_name):
    # Fetch the NSE data
    stock = fetch_data(scrip_name)

    # Apply the strategies individual
    stock = apply_moving_average_strategy(stock)
    stock = apply_rsi_strategy(stock)
    stock = apply_macd_strategy(stock)
    stock = apply_engulfing_pattern(stock)

    # Get only 2021 data for further analysis
    # import pdb; pdb.set_trace()
    stock = stock[stock.index >= str(date(2023,1,1))]

    # stock = print(stock)

    # Merge the strategies to create a final BUY/SELL/HOLD indicator
    stock = apply_trading_algo(stock)

    # # Plot the buy/sell recommendations on 2021 data
    show_signals(scrip_name, stock)
    
    return stock