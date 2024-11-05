import config
import discord
import requests
bot = discord.Bot()

ALPHA_VANTAGE_API_KEY = config.ALPHA_VANTAGE_API_KEY
DISCORD_TOKEN = config.DISCORD_TOKEN

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(guild_ids=[config.GUILD_ID]) 
async def hello(ctx):
    await ctx.respond('Hello! I am a simple bot!')

@bot.slash_command(guild_ids=[config.GUILD_ID])
async def insult(ctx, user: discord.User):
    await ctx.respond(f'Uy {user.mention}, ambaho ng utot mo!')


# Command for generating chart data
@bot.slash_command(guild_ids=[config.GUILD_ID])
async def chart(ctx, symbol: str, function_input: str):
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
        await ctx.respond('Error fetching data')
        return
    else:
        print(response.json())
        await ctx.respond('Data fetched')

bot.run(DISCORD_TOKEN)
