from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import discord
from discord.ext import commands
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

@bot.slash_command(name="help", description="Learn more about reo-bot and its commands") 
async def help(ctx):
    embed = discord.Embed(title="I'm `reo-bot`, nice to meet you! 👋", description="I can provide real-time financial charts and ticker data for stocks and assets.", color=discord.Colour.blurple())
    embed.add_field(name="`/help`", value="View all commands", inline=False)
    embed.add_field(name="`/info`", value="Get information about a stock.", inline=False)
    embed.add_field(name="`/crypto_price`", value="Get the current price of a cryptocurrency.", inline=False)
    embed.add_field(name="`/stock_price`", value="Get the current price of a stock.", inline=False)
    embed.add_field(name="`/day_chart`", value="Generate the latest intraday chart for a given symbol.", inline=False)
    embed.add_field(name="`/week_chart`", value="Generate this week's chart for a given symbol.", inline=False)
    embed.add_field(name="`/month_chart`", value="Generate the latest month chart for a given symbol.", inline=False)
    embed.add_field(name="`/year_chart`", value="Generate the latest year chart for a given symbol.", inline=False)
    embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="Fun fact: I'm named after Reo Mikage from the anime Blue Lock, hence the chameleon icon!")
    await ctx.respond(embed=embed)

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

            embed = discord.Embed(title=f'Current Price of {symbol.upper()}', description=f'The current price of {symbol.upper()} is ${"{:.2f}".format(round(float(price),2))}.', color=discord.Colour.blurple())
            embed.add_field(name='Learn More', value=f'[View more information about {symbol.upper()}](https://www.tradingview.com/symbols/{symbol.upper()}USD)', inline=False)
            embed.set_footer(text='Data provided by Alpha Vantage')
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)

            await ctx.respond(embed=embed)

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

            embed = discord.Embed(title=f'Current Price of {symbol.upper()}', description=f'The current price of {symbol.upper()} is ${"{:.2f}".format(round(float(price),2))}.', color=discord.Colour.blurple())
            embed.add_field(name='Learn More', value=f'[View more information about {symbol.upper()}](https://www.tradingview.com/symbols/{symbol.upper()})', inline=False)
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
            embed.set_footer(text='Data provided by Alpha Vantage')

            await ctx.respond(embed=embed)

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
            embed = discord.Embed(title=f'Latest Day Chart for {symbol.upper()}', description=f'Here is the latest day chart for {symbol.upper()}.', color=discord.Colour.blurple())
            embed.add_field(name='Learn More', value=f'[View more information about {symbol.upper()}](https://www.tradingview.com/symbols/{symbol.upper()})', inline=False)
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
            embed.set_image(url=f"attachment://{symbol.upper()}_chart.png")
            embed.set_footer(text='Data provided by Alpha Vantage')
            await ctx.send(embed=embed, file=discord.File(buf, f"{symbol.upper()}_chart.png"))


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
            embed = discord.Embed(title=f'Latest Week Chart for {symbol.upper()}', description=f'Here is the latest week chart for {symbol.upper()}.', color=discord.Colour.blurple())
            embed.add_field(name='Learn More', value=f'[View more information about {symbol.upper()}](https://www.tradingview.com/symbols/{symbol.upper()})', inline=False)
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
            embed.set_image(url=f"attachment://{symbol.upper()}_chart.png")
            embed.set_footer(text='Data provided by Alpha Vantage')
            await ctx.send(embed=embed, file=discord.File(buf, f"{symbol.upper()}_chart.png"))
            

# Command for generating month chart data
@bot.slash_command(name='month_chart', description='Generate the latest month chart for a given symbol and function')
async def month_chart (
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g. 'AAPL' for Apple")
):
    await ctx.respond(f'Fetching the latest month chart for {symbol.upper()}...')

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
            # Get chart for this month
            time_series = response.json().get('Time Series (Daily)', {})
            if not time_series:
                await ctx.respond('No data available for the given symbol.')
                return

            # Filter data for the past 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            month_data = {date: data for date, data in time_series.items() if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date}

            if not month_data:
                await ctx.respond('No data available for the past 30 days.')
                return

            # Sort the data in ascending order
            month_data = dict(sorted(month_data.items()))

            # Prepare data for candlestick chart
            df = pd.DataFrame.from_dict(month_data, orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)

            # Create buffer
            buf = BytesIO()
            
            # Generate candlestick chart
            mpf.plot(df, type='candle', style='charles', title=f'{symbol.upper()} Stock Price', ylabel='Price ($)', savefig=dict(fname=buf, format='png'))
            buf.seek(0)

            # Send to discord channel
            embed = discord.Embed(title=f'Latest Month Chart for {symbol.upper()}', description=f'Here is the latest month chart for {symbol.upper()}.', color=discord.Colour.blurple())
            embed.add_field(name='Learn More', value=f'[View more information about {symbol.upper()}](https://www.tradingview.com/symbols/{symbol.upper()})', inline=False)
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
            embed.set_image(url=f"attachment://{symbol.upper()}_chart.png")
            embed.set_footer(text='Data provided by Alpha Vantage')
            await ctx.send(embed=embed, file=discord.File(buf, f"{symbol.upper()}_chart.png"))

# Command for generating year chart data
@bot.slash_command(name='year_chart', description='Generate the latest year chart for a given symbol and function')

async def year_chart (
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g. 'AAPL' for Apple")
):

    await ctx.respond(f'Fetching the latest year chart for {symbol.upper()}...')

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
            # Get chart for this year
            time_series = response.json().get('Time Series (Daily)', {})
            if not time_series:
                await ctx.respond('No data available for the given symbol.')
                return

            # Filter data for the past 365 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            year_data = {date: data for date, data in time_series.items() if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date}

            if not year_data:
                await ctx.respond('No data available for the past 365 days.')
                return

            # Sort the data in ascending order
            year_data = dict(sorted(year_data.items()))

            # Prepare data for candlestick chart
            df = pd.DataFrame.from_dict(year_data, orient='index')
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.astype(float)

            # Create buffer
            buf = BytesIO()

            # Generate candlestick chart
            mpf.plot(df, type='candle', style='charles', title=f'{symbol.upper()} Stock Price', ylabel='Price ($)', savefig=dict(fname=buf, format='png'))
            buf.seek(0)

            # Send to discord channel
            embed = discord.Embed(title=f'Latest Year Chart for {symbol.upper()}', description=f'Here is the latest year chart for {symbol.upper()}.', color=discord.Colour.blurple())
            embed.add_field(name='Learn More', value=f'[View more information about {symbol.upper()}](https://www.tradingview.com/symbols/{symbol.upper()})', inline=False)
            embed.set_image(url=f"attachment://{symbol.upper()}_chart.png")
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
            embed.set_footer(text='Data provided by Alpha Vantage')
            await ctx.send(embed=embed, file=discord.File(buf, f"{symbol.upper()}_chart.png"))

@bot.slash_command(name='info', description='Get information about a stock.')
async def info(ctx, symbol: str=discord.Option(description="The stock symbol to get information for, e.g. 'AAPL' for Apple")):

    await ctx.respond(f'Fetching information for {symbol.upper()}...')

    # Fetch from alpha vantage API
    url = f'https://www.alphavantage.co/query'
    params = {
        'function':'OVERVIEW',
        'symbol': symbol.upper(),
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'compact'
    }

    response = requests.get(url, params=params)

    # Check if response is successful
    if response.status_code != 200:
        await ctx.respond('Error fetching info data. Please try again.')
        return
    else:
        data = response.json()
        if 'Error Message' in response.json():
            await ctx.respond('Invalid inputs in info command. Please enter a valid symbol.')
        else:
            # Access data from the dictionary
            company_name = data.get('Name', 'N/A')
            sector = data.get('Sector', 'N/A')
            market_cap = data.get('MarketCapitalization', 'N/A')
            pe_ratio = data.get('PERatio', 'N/A')
            eps = data.get('EPS', 'N/A')
            dividend_per_share = data.get('DividendPerShare', 'N/A')
            dividend_yield = data.get('DividendYield', 'N/A')
            week_52_high = data.get('52WeekHigh', 'N/A')
            week_52_low = data.get('52WeekLow', 'N/A')
            website = data.get('OfficialSite', 'N/A') 

            # Create an embed to display information
            embed = discord.Embed(title=f'{company_name}', color=discord.Colour.blurple())
            embed.add_field(name='Sector', value=sector.capitalize(), inline=False)
            embed.add_field(name='Market Cap', value=f"${int(market_cap):,}" if market_cap != "N/A" else market_cap , inline=False)
            embed.add_field(name='P/E Ratio', value=pe_ratio, inline=False)
            embed.add_field(name='EPS', value=eps, inline=False)
            embed.add_field(name='Dividend Per Share', value=f"${dividend_per_share}", inline=False)
            embed.add_field(name='Dividend Yield', value='{:.2%}'.format(float(dividend_yield)) if dividend_yield != "N/A" else dividend_yield, inline=False)
            embed.add_field(name='52 Week High', value=f"${week_52_high}", inline=False)
            embed.add_field(name='52 Week Low', value=f"${week_52_low}", inline=False)
            embed.add_field(name='Website', value=f'[Official Website for {company_name}]({website})', inline=False)
            embed.set_author(name="reo-bot", icon_url=bot.user.display_avatar.url)
            embed.set_footer(text='Data provided by Alpha Vantage')
            await ctx.respond(embed=embed)

bot.run(DISCORD_TOKEN)