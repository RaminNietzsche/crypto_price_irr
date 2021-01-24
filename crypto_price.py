from flask import Flask, request, render_template
import requests
import json
import datetime

import plotly.graph_objects as go

app = Flask(__name__)

@app.route("/")
@app.route("/<currency>/")
def index(currency = "BTC"):
    return render_template("index.html", currency=currency, crypto_price=get_crypto_price(currency), usd=get_usd_price())

@app.route("/crypto/update/")
@app.route("/crypto/update/<currency>/")
def update_price(currency = "BTC"):
    return get_crypto_price(currency)

@app.route("/usd/update/")
def update_usd_price():
    return get_usd_price()

def get_usd_price():
    api = "https://call7.tgju.org/ajax.json"
    response = json.loads(requests.get(api).content)
    return str(response["current"]["price_dollar_rl"]['p'])

def get_crypto_price(currency = "BTC"):
    api = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms={currency}&tsyms=USD"
    response = json.loads(requests.get(api).content)
    return str(response[currency]['USD'])

@app.route("/history/crypto/")
@app.route("/history/crypto/<currency>")
def historical_crypto(currency = "BTC"):
    df = get_historical_crypto(currency)
    graph_data = go.Figure(
        data=[
            go.Candlestick(
            x=df['time'],
            open=df['open'], 
            high=df['high'],
            low=df['low'], 
            close=df['close']
            ),
        ]
    )

    return graph_data.to_html()
    
def get_historical_crypto(currency = "BTC"): 
    api = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={currency}&tsym=USD"
    response = json.loads(requests.get(api).content)
    df = {}
    for item in response["Data"]["Data"][:30]:
        if 'time' not in df:
            df['time'] = [datetime.datetime.fromtimestamp(item['time'])]
        else:
            df['time'].append(datetime.datetime.fromtimestamp(item['time']))

        if 'open' not in df:
            df['open'] = [item['open']]
        else:
            df['open'].append(item['open'])

        if 'high' not in df:
            df['high'] = [item['high']]
        else:
            df['high'].append(item['high'])

        if 'low' not in df:
            df['low'] = [item['low']]
        else:
            df['low'].append(item['low'])

        if 'close' not in df:
            df['close'] = [item['close']]
        else:
            df['close'].append(item['close'])

    return df


@app.route("/history/usd/")
def historical_usd():
    df = get_historical_usd()
    graph_data = go.Figure(
        data=[
            go.Candlestick(
            x=df['time'],
            open=df['open'], 
            high=df['high'],
            low=df['low'], 
            close=df['close']
            ),
        ]
    )

    return graph_data.to_html()

def get_historical_usd():
    api = f"https://api.accessban.com/v1/market/indicator/summary-table-data/price_dollar_rl"
    response = json.loads(requests.get(api).content)
    df = {}
    for item in response["data"][:30]:
        if 'time' not in df:
            df['time'] = [datetime.datetime.strptime(item[6], '%Y/%m/%d')]
        else:
            df['time'].append(datetime.datetime.strptime(item[6], '%Y/%m/%d'))

        if 'open' not in df:
            df['open'] = [float(item[0].replace(",",""))]
        else:
            df['open'].append(float(item[0].replace(",","")))

        if 'high' not in df:
            df['high'] = [float(item[2].replace(",",""))]
        else:
            df['high'].append(float(item[2].replace(",","")))

        if 'low' not in df:
            df['low'] = [float(item[1].replace(",",""))]
        else:
            df['low'].append(float(item[1].replace(",","")))

        if 'close' not in df:
            df['close'] = [float(item[3].replace(",",""))]
        else:
            df['close'].append(float(item[3].replace(",","")))
    
    return df


@app.route("/history/crypto_ir/")
def historical_crypto_ir():
    crypto_df = get_historical_crypto()
    usd_df = get_historical_usd()

    df = {}
    df['time'] = crypto_df['time']
    df['open'] = [x*y for x,y in zip(usd_df['open'], crypto_df['open'])]
    df['high'] = [x*y for x,y in zip(usd_df['high'], crypto_df['high'])]
    df['low']  = [x*y for x,y in zip(usd_df['low'], crypto_df['low'])]
    df['close'] = [x*y for x,y in zip(usd_df['close'], crypto_df['close'])]

    graph_data = go.Figure(
        data=[
            go.Candlestick(
            x=df['time'],
            open=df['open'], 
            high=df['high'],
            low=df['low'], 
            close=df['close']
            ),
        ]
    )

    return graph_data.to_html()    

if __name__ == "__main__":
    app.run('0.0.0.0', port=8080, debug=True)