# Imports
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
from pandas import ExcelWriter
import yfinance as yf
import pandas as pd
import datetime
import time
import os.path

import json
import requests
import finnhub

from datetime import date
from pathlib import Path
yf.pdr_override()


# Setup client
finnhub_client = finnhub.Client(api_key="sandbox_c2sq92aad3ic1qis94eg")
# finnhub_client = finnhub.Client(api_key="btvkm4748v6uc2r6kpp0")

today = date.today()
d1 = today.strftime("%Y%m%d")

def make_dir(index_name):
    if os.path.isdir(f'data/{d1}/{index_name}/'):
        return False
    else:
        Path(f'data/{d1}/{index_name}/').mkdir(parents=True, exist_ok=True)
        return True
    
# Stock symbols
#print(finnhub_client.stock_symbols('US')[0:5])
#print(finnhub_client.stock_symbols('HK')[0:5])
    
def get_tickers(index_name):
    if index_name == 'hsi':
        df = pd.DataFrame(finnhub_client.stock_symbols('HK'))
        tickers = df['symbol'].values.tolist()
    elif index_name == 'dow':
        tickers = si.tickers_dow()
    elif index_name == 'sp500':
        tickers = si.tickers_sp500()
    elif index_name == 'nasdaq':
        tickers = si.tickers_nasdaq()
            
    if index_name == 'dow' or index_name == 'sp500' or index_name == 'nasdaq' :
        tickers = [item.replace(".", "-") for item in tickers] # Yahoo Finance uses dashes instead of dots

    return tickers

def get_index_ticker(index_name):
    if index_name == 'hsi':
        return '^HSI'
    elif index_name == 'dow':
        return '^DJI'
    elif index_name == 'sp500':
        return '^GSPC'
    elif index_name == 'nasdaq':
        return '^IXIC'
    
def screen(index_name):
    # make directory
    download_data = make_dir(index_name)
    
    # Variables
    
    tickers = get_tickers(index_name)
    index_ticker = get_index_ticker(index_name)
    
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    exportList = pd.DataFrame(columns=['Stock', "RS_Rating", "50 Day MA", "150 Day Ma", "200 Day MA", "52 Week Low", "52 week High"])
    returns_multiples = []
    
    # Index Returns
    index_df = pdr.get_data_yahoo(index_ticker, start_date, end_date)
    index_df['Percent Change'] = index_df['Adj Close'].pct_change()
    index_return = (index_df['Percent Change'] + 1).cumprod()[-1]
    
    list_length = len(tickers)
    count = 0
    
    if (download_data):
        print('Downloading data')
    else:
        print('Reading local data')
    
    # Find top 30% performing stocks (relative to the index)
    for ticker in tickers:
        count += 1
        
        if (download_data or not os.path.isfile(f'data/{d1}/{index_name}/{ticker}_.csv')):
            # Download historical data as CSV for each stock (makes the process faster)
            df = pdr.get_data_yahoo(ticker, start_date, end_date)
            df.to_csv(f'data/{d1}/{index_name}/{ticker}_.csv')
            print('Downloading data from Yahoo')
        else:
            # Read csv downloaded
            df = pd.read_csv(f'data/{d1}/{index_name}/{ticker}_.csv', index_col=0)
            print('Reading local data')
    
        # Calculating returns relative to the market (returns multiple)
        df['Percent Change'] = df['Adj Close'].pct_change()
        if not df.empty:
            stock_return = (df['Percent Change'] + 1).cumprod()[-1]
        
        returns_multiple = round((stock_return / index_return), 2)
        returns_multiples.extend([returns_multiple])
        
        print (f'Ticker: {ticker}; Returns Multiple against {index_name}: {returns_multiple} \t {count} / {list_length}\n')
        time.sleep(0.02)
    
    # Creating dataframe of only top 30%
    rs_df = pd.DataFrame(list(zip(tickers, returns_multiples)), columns=['Ticker', 'Returns_multiple'])
    rs_df['RS_Rating'] = rs_df.Returns_multiple.rank(pct=True) * 100
    rs_df = rs_df[rs_df.RS_Rating >= rs_df.RS_Rating.quantile(.70)]
    
    # Checking Minervini conditions of top 30% of stocks in given list
    rs_stocks = rs_df['Ticker']
    
    list_length = len(rs_stocks)
    count = 0
    for stock in rs_stocks:    
        try:
            count += 1
            df = pd.read_csv(f'data/{d1}/{index_name}/{stock}_.csv', index_col=0)
            sma = [50, 150, 200]
            for x in sma:
                df["SMA_"+str(x)] = round(df['Adj Close'].rolling(window=x).mean(), 2)
            
            # Storing required values 
            currentClose = df["Adj Close"][-1]
            moving_average_50 = df["SMA_50"][-1]
            moving_average_150 = df["SMA_150"][-1]
            moving_average_200 = df["SMA_200"][-1]
            low_of_52week = round(min(df["Low"][-260:]), 2)
            high_of_52week = round(max(df["High"][-260:]), 2)
            RS_Rating = round(rs_df[rs_df['Ticker']==stock].RS_Rating.tolist()[0])
            
            try:
                moving_average_200_20 = df["SMA_200"][-20]
            except Exception:
                moving_average_200_20 = 0
    
            # Condition 1: Current Price > 150 SMA and > 200 SMA
            condition_1 = currentClose > moving_average_150 > moving_average_200
            
            # Condition 2: 150 SMA and > 200 SMA
            condition_2 = moving_average_150 > moving_average_200
    
            # Condition 3: 200 SMA trending up for at least 1 month
            condition_3 = moving_average_200 > moving_average_200_20
            
            # Condition 4: 50 SMA> 150 SMA and 50 SMA> 200 SMA
            condition_4 = moving_average_50 > moving_average_150 > moving_average_200
            
            # Condition 5: Current Price > 50 SMA
            condition_5 = currentClose > moving_average_50
            
            # Condition 6: Current Price is at least 30% above 52 week low
            condition_6 = currentClose >= (1.3*low_of_52week)
            
            # Condition 7: Current Price is within 25% of 52 week high
            condition_7 = currentClose >= (.75*high_of_52week)
            
            # If all conditions above are true, add stock to exportList
            if(condition_1 and condition_2 and condition_3 and condition_4 and condition_5 and condition_6 and condition_7):
                exportList = exportList.append({'Stock': stock, "RS_Rating": RS_Rating ,"50 Day MA": moving_average_50, "150 Day Ma": moving_average_150, "200 Day MA": moving_average_200, "52 Week Low": low_of_52week, "52 week High": high_of_52week}, ignore_index=True)
                count += 1
                print (f"{stock} made the Minervini requirements \t {count} / {list_length}\n")
        except Exception as e:
            print (e)
            print(f"Could not gather data on {stock}")
    
    exportList = exportList.sort_values(by='RS_Rating', ascending=False)
    print('\n', exportList)
    
    return exportList
    
if __name__ == '__main__':
    # screen()
    # Stock symbols
    df = pd.DataFrame(finnhub_client.stock_symbols('HK'))
    tickers = df['symbol'].values.tolist()
    # print(finnhub_client.quote('0005.HK'))
    # {'c': 48.8, 'h': 49.7, 'l': 48.65, 'o': 49.6, 'pc': 49.15, 't': 1622770200}
    print(finnhub_client.quote('AMC')) # 30 API call per second
    # {'c': 59.04, 'h': 64.71, 'l': 56.73, 'o': 58.39, 'pc': 57, 't': 1623787201}
    # print(json.loads(df))