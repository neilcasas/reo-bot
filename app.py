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

@bot.slash_command()
async def insult(ctx, user: discord.User):
    await ctx.respond(f'Uy {user.mention}, ambaho ng utot mo!')

# Command for generating weekly chart data
@bot.slash_command(name='weekly_chart', description='Generate this week\'s chart for a given symbol and function')
async def weekly_chart (
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g. 'AAPL' for Apple")
):

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
            await ctx.send(file=discord.File(buf, f"{symbol.upper()}_chart.png"))

bot.run(DISCORD_TOKEN)
