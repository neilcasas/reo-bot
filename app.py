import config
import discord
import requests
import matplotlib.pyplot as plt
from io import BytesIO

bot = discord.Bot()

ALPHA_VANTAGE_API_KEY = config.ALPHA_VANTAGE_API_KEY
DISCORD_TOKEN = config.DISCORD_TOKEN

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command() 
async def hello(ctx):
    await ctx.respond('Hello! I am a simple bot!')

@bot.slash_command()
async def insult(ctx, user: discord.User):
    await ctx.respond(f'Uy {user.mention}, ambaho ng utot mo!')

# Command for generating chart data
@bot.slash_command(name='chart', description='Generate chart data for a given symbol and function')
async def chart(
    ctx,
    symbol: str = discord.Option(description="The stock symbol to get data for, e.g., 'AAPL' for Apple"),
    function_input: str = discord.Option(description="The time series function, e.g., 'INTRADAY', 'DAILY', 'WEEKLY', 'MONTHLY'")
):
    # Get financial data
    url = f'https://www.alphavantage.co/query'
    params = {
       'function': f'TIME_SERIES_{function_input.upper()}',
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
            
            # Create buffer
            buf = BytesIO()

            # Generate chart
            plt.plot([1,2,3],[4,5,6])
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            # Send to discord channel
            print(response.json())
            await ctx.send(file=discord.File(buf, f"{symbol.upper()}_{function_input.upper()}_chart.png"))

bot.run(DISCORD_TOKEN)
