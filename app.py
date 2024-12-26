from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import discord
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import mplfinance as mpf
import pandas as pd

# Load .env
load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command() 
async def hello(ctx):
    await ctx.respond('Hello! I am a simple bot!')

# Command for getting the current price of a cryptocurrency
@bot.slash_command(name='crypto_price', description='Get the current price of a cryptocurrency')
async def crypto_price (
    ctx,
    symbol: str = discord.Option(description="The cryptocurrency symbol to get data for, e.g. 'BTC' for Bitcoin")
):
    await ctx.respond(f'Fetching the current price of {symbol.upper()}...')
    # Get financial data
    url = f'https://www.alphavantage.co/query'
    params = {
        'function':'CURRENCY_EXCHANGE_RATE',
        'from_currency': symbol.upper(),
        'to_currency': 'USD',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    response = requests.get(url, params=params)

    # Check if response is successful
    if response.status_code != 200:
        await ctx.respond('Error fetching cryptocurrency price. Please try again.')
        return
    else:
        if 'Error Message' in response.json():
            await ctx.respond('Invalid inputs in cryptocurrency price command. Please enter a valid symbol.')
        else:
            # Get cryptocurrency price
            price = response.json().get('Realtime Currency Exchange Rate', {}).get('5. Exchange Rate')
            if not price:
                await ctx.respond('No data available for the given symbol.')
                return

            await ctx.respond(f'The current price of {symbol.upper()} is ${"{:.2f}".format(round(float(price),2))}.')

# Command for getting the current price of a stock
@bot.slash_command(name='stock_price', description='Get the current price of a stock')
async def stock_price (
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g. 'AAPL' for Apple")
):
    await ctx.respond(f'Fetching the current price of {symbol.upper()}...')
    # Get financial data
    url = f'https://www.alphavantage.co/query'
    params = {
        'function':'GLOBAL_QUOTE',
        'symbol': symbol.upper(),
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    response = requests.get(url, params=params)

    # Check if response is successful
    if response.status_code != 200:
        await ctx.respond('Error fetching stock price. Please try again.')
        return
    else:
        if 'Error Message' in response.json():
            await ctx.respond('Invalid inputs in stock price command. Please enter a valid symbol.')
        else:
            # Get stock price
            price = response.json().get('Global Quote', {}).get('05. price')
            if not price:
                await ctx.respond('No data available for the given symbol.')
                return

            await ctx.respond(f'The current price of {symbol.upper()} is ${"{:.2f}".format(round(float(price),2))}.')

# Command for generating daily chart data
@bot.slash_command(name='day_chart', description='Generate the latest intraday chart for a given symbol and function')
async def day_chart (
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g. 'AAPL' for Apple")
):

    await ctx.respond(f'Fetching the latest day chart for {symbol.upper()}...')
    # Get financial data
    url = f'https://www.alphavantage.co/query'
    params = {
        'function':'TIME_SERIES_INTRADAY',
        'symbol': symbol.upper(),
        'interval': '5min',
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    response = requests.get(url, params=params)

    # Check if response is successful
    if response.status_code != 200:
        await ctx.respond('Error fetching chart data. Please try again.')
        return
    else:
        if 'Error Message' in response.json():
            await ctx.respond('Invalid inputs in chart command. Please enter a valid symbol or function.')
        else:
            # Get chart for today
            time_series = response.json().get('Time Series (5min)', {})
            if not time_series:
                await ctx.respond('No data available for the given symbol.')
                return

            # Prepare candlestick chart
            df = pd.DataFrame.from_dict(time_series, orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)

            # Create buffer
            buf = BytesIO()

            # Generate candlestick chart
            mpf.plot(df, type='candle', style='charles', title=f'{symbol.upper()} Stock Price', ylabel='Price ($)', savefig=dict(fname=buf, format='png'))
            buf.seek(0)

            # Send to discord channel
            print(time_series)
            await ctx.send(f'Here is the latest day chart for {symbol.upper()}:')
            await ctx.send(file=discord.File(buf, f"{symbol.upper()}_chart.png"))

# Command for generating weekly chart data
@bot.slash_command(name='week_chart', description='Generate the latest week chart for a given symbol and function')
async def week_chart (
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g. 'AAPL' for Apple")
):

    await ctx.respond(f'Fetching the latest week chart for {symbol.upper()}...')
    # Get financial data
    url = f'https://www.alphavantage.co/query'
    params = {
       'function':'TIME_SERIES_DAILY',
        'symbol': symbol.upper(),
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'compact'
    }

    response = requests.get(url, params=params)

    # Check if response is successful
    if response.status_code != 200:
        await ctx.respond('Error fetching chart data. Please try again.')
        return
    else:
        if 'Error Message' in response.json():
            await ctx.respond('Invalid inputs in chart command. Please enter a valid symbol or function.')
        else:
            # Get chart for this week
            time_series = response.json().get('Time Series (Daily)', {})
            if not time_series:
                await ctx.respond('No data available for the given symbol.')
                return

            # Filter data for the past 7 days
            end_date = datetime.now() # took today's date
            start_date = end_date - timedelta(days=7) # took 7 days before today's date
            week_data = {date: data for date, data in time_series.items() if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date}

            if not week_data:
                await ctx.respond('No data available for the past 7 days.')
                return

            # Sort the data in ascending order
            week_data = dict(sorted(week_data.items()))

            # Prepare data for candlestick chart
            df = pd.DataFrame.from_dict(week_data, orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)

            # Create buffer
            buf = BytesIO()

            # Generate candlestick chart
            mpf.plot(df, type='candle', style='charles', title=f'{symbol.upper()} Stock Price', ylabel='Price ($)', savefig=dict(fname=buf, format='png'))
            buf.seek(0)

            # Send to discord channel
            print(week_data)
            await ctx.send(f'Here is the latest week chart for {symbol.upper()}:')
            await ctx.send(file=discord.File(buf, f"{symbol.upper()}_chart.png"))

bot.run(DISCORD_TOKEN)
