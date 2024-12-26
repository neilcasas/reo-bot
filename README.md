# reo-bot
reo-bot is a Discord bot that assists in your financial ventures by providing real-time financial charts and ticker data for stocks and assets.

## Features

- Get the current price of a cryptocurrency
- Get the current price of a stock
- Generate intraday, weekly, monthly, and yearly charts for a given stock symbol
- Get detailed information about a stock

## Commands

- `/help` - View all commands
- `/crypto_price` - Get the current price of a cryptocurrency
- `/stock_price` - Get the current price of a stock
- `/day_chart` - Generate the latest intraday chart for a given symbol
- `/week_chart` - Generate this week's chart for a given symbol
- `/month_chart` - Generate the latest month chart for a given symbol
- `/year_chart` - Generate the latest year chart for a given symbol
- `/info` - Get information about a stock

## Prerequisites

- Python 3.12 or higher
- A Discord bot token
- An Alpha Vantage API key

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/reo-bot.git
    cd reo-bot
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a  file in the project directory and add your Discord bot token and Alpha Vantage API key:
    ```env
    DISCORD_TOKEN=your_discord_token
    ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
    ```

## Running the Bot
1. Ensure your virtual environment is activated.
2. Run the bot:
    ```sh
    python app.py
    ```

The bot should now be running and ready to use in your Discord server.

## Todo
- Watchlist
