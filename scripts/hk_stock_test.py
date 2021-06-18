# Imports
from pandas_datareader import data as pdr
from yahoo_fin import stock_info as si
from pandas import ExcelWriter
import yfinance as yf
import pandas as pd
import datetime
import time
yf.pdr_override()

# make directory
from pathlib import Path
Path(f'../data/hk_stock').mkdir(parents=True, exist_ok=True)

# Variables

# custom code for gettin tickers
import wikipedia
#print(wikipedia.summary("List of companies listed on the Hong Kong Stock Exchange"))
#wikipedia.search("List of companies listed on the Hong Kong Stock Exchange")
page = wikipedia.page("List of companies listed on the Hong Kong Stock Exchange").html()

import re

result = re.search('SEHK</a>:&#1(.*)<a ', page)
print(result.group(1))

#print(page[0])
