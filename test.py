import pandas as pd
from finnhub import client as Finnhub
from plotly.offline import plot, iplot, init_notebook_mode
import plotly.graph_objs as go

init_notebook_mode()

client = Finnhub.Client(api_key="bpm660nrh5r8rtje5kh0")
source = client.stock_candle(symbol="AAPL", resolution="15", count=400)

df = pd.DataFrame(data=source)
df.columns = ["Close","High","Low","Open","Status","Date","Volume"]
df['Date'] = pd.to_datetime(df['Date'], unit="s")
df["100ma"] = df["Close"].rolling(window=100, min_periods=0).mean()
df = df.set_index('Date')
df['2020-03'].Close.mean()
