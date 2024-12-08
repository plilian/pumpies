import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import os
import asyncio
import urllib.parse



load_dotenv("tg.env")

user_last_command_time = {}
RATE_LIMIT_SECONDS = 1.5

async def check_rate_limit(update: Update) -> bool:
    user_id = update.message.from_user.id
    current_time = datetime.now()

    if user_id in user_last_command_time:
        last_command_time = user_last_command_time[user_id]
        time_difference = (current_time - last_command_time).total_seconds()

        if time_difference < RATE_LIMIT_SECONDS:
            return False

    user_last_command_time[user_id] = current_time
    return True



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    welcome_message = (
        "👋 **Welcome to Coin Lens Bot!**\n\n"
        "I'm here to help you stay updated with the latest cryptocurrency data. "
        "Use the following commands to interact with me:\n\n"

        "💡 **Examples:**\n"
        "   `/search bitcoin`\n"
        "   `/trending`\n"
        "   `/dominance`\n"
        "   `/companies ethereum or /companies bitcoin`\n"
        "   `/categories`\n"
        "   `/coin_details btc`\n"
        "   `/bop btc days 1 or 7 or 14`\n\n"

        "If you have any questions or need further assistance, feel free to reach out!"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    if context.args:
        query = " ".join(context.args)
        search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
        headers = {
            "accept": "application/json",
        }

        try:
            search_response = requests.get(search_url, headers=headers)
            search_response.raise_for_status()
            search_data = search_response.json()

            if search_data.get("coins"):
                first_coin = search_data["coins"][0]
                coin_id = first_coin["api_symbol"]
                name = first_coin["name"]
                market_cap_rank = first_coin.get("market_cap_rank", "N/A")
                symbol = first_coin["symbol"]
                await asyncio.sleep(1.2)
                price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&precision=10"
                price_response = requests.get(price_url, headers=headers)
                price_response.raise_for_status()
                price_data = price_response.json()

                price_info = price_data.get(coin_id, {})
                usd_price = price_info.get("usd", "N/A")
                usd_market_cap = price_info.get("usd_market_cap", "N/A")
                usd_24h_vol = price_info.get("usd_24h_vol", "N/A")
                usd_24h_change = price_info.get("usd_24h_change", "N/A")

                await update.message.reply_text(
                    f"🔎 **Search Results**\n\n"
                    f"🆔 **ID**: `{coin_id}`\n"
                    f"🏷️ **Name**: *{name}*\n"
                    f"📊 **Market Cap Rank**: #{market_cap_rank}\n"
                    f"💠 **Symbol**: `{symbol.upper()}`\n\n"
                    f"💵 **Price Details (USD):**\n"
                    f"💲 **Current Price**: `${usd_price:,.10f}`\n"
                    f"💰 **Market Cap**: `${usd_market_cap:,.2f}`\n"
                    f"📈 **24h Volume**: `${usd_24h_vol:,.2f}`\n"
                    f"📉 **24h Change**: `{usd_24h_change:.2f}%`\n",
                    parse_mode="Markdown"
                )

            else:
                await update.message.reply_text("No results found for your query. Please try again.")

        except requests.exceptions.RequestException as e:
            await update.message.reply_text(f"An error occurred while fetching data: {e}")
    else:
        await update.message.reply_text("Please provide a query. Usage: /search <your query>")


async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    url = "https://api.coingecko.com/api/v3/search/trending"

    headers = {
        "accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        coins = data.get("coins", [])[:5]
        if not coins:
            await update.message.reply_text("No trending coins found at the moment.")
            return

        message = "Trending Coins:\n\n"
        for coin_data in coins:
            item = coin_data.get("item", {})
            name = item.get("name", "N/A")
            symbol = item.get("symbol", "N/A")
            rank = item.get("market_cap_rank", "N/A")
            usd_price = item.get("data", {}).get("price", "N/A")
            if isinstance(usd_price, (float, int)):
                if usd_price > 1:
                    usd_price = f"{usd_price:.2f}"
                elif 0.0001 < usd_price <= 1:
                    usd_price = f"{usd_price:.6f}"
                elif usd_price <= 0.0001:
                    usd_price = f"{usd_price:.10f}"
            else:
                usd_price = "N/A"
            market_cap = item.get("data", {}).get("market_cap", "N/A")
            market_cap_btc = item.get("data", {}).get("market_cap_btc", "N/A")
            total_volume = item.get("data", {}).get("total_volume", "N/A")
            total_volume_btc = item.get("data", {}).get("total_volume_btc", "N/A")


            message += (
                f"🔥 **Trending Coins** 🔥\n\n"
                f"🏷️ **Name**: *{name}*\n"
                f"💠 **Symbol**: `{symbol.upper()}`\n"
                f"📊 **Rank**: #{rank}\n\n"
                f"💵 **Price Details (USD):**\n"
                f"💲 **Current Price**: `${usd_price}`\n"
                f"💰 **Market Cap**: `${market_cap}`\n"
                f"🪙 **Market Cap (BTC)**: `{market_cap_btc} BTC`\n"
                f"📈 **Total Volume (USD)**: `${total_volume}`\n"
                f"🪙 **Total Volume (BTC)**: `{total_volume_btc:} BTC`\n"
                "---------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def dominance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    url = "https://api.coingecko.com/api/v3/global"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("data", {})

        active_cryptocurrencies = data.get("active_cryptocurrencies", "N/A")
        market_cap_percentage = data.get("market_cap_percentage", {})
        btc_dominance = market_cap_percentage.get("btc", "N/A")
        eth_dominance = market_cap_percentage.get("eth", "N/A")
        usdt_dominance = market_cap_percentage.get("usdt", "N/A")
        market_cap_change_24h = data.get("market_cap_change_percentage_24h_usd", "N/A")

        message = (
            f"📊 **Cryptocurrency Market Dominance** 📊\n\n"
            f"🪙 **Active Cryptocurrencies**: `{active_cryptocurrencies}`\n"
            f"⚡ **BTC Dominance**: `{btc_dominance:.2f}%`\n"
            f"🔥 **ETH Dominance**: `{eth_dominance:.2f}%`\n"
            f"💵 **USDT Dominance**: `{usdt_dominance:.2f}%`\n"
            f"📈 **24h Market Cap Change**: `{market_cap_change_24h:.2f}%`\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def companies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    if not context.args:
        await update.message.reply_text(
            "Please specify a coin ID (e.g., bitcoin or ethereum). Usage: /companies <coin_id>"
        )
        return

    coin_id = context.args[0]
    url = f"https://api.coingecko.com/api/v3/companies/public_treasury/{coin_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        total_holdings = data.get("total_holdings", "N/A")
        total_value_usd = data.get("total_value_usd", "N/A")
        market_cap_dominance = data.get("market_cap_dominance", "N/A")

        message = (
            f"🏦 **Companies Holding {coin_id.capitalize()}** 🏦\n\n"
            f"📊 **Total Holdings**: `{total_holdings}`\n"
            f"💵 **Total Value (USD)**: `${total_value_usd:,.2f}`\n"
            f"🌍 **Market Cap Dominance**: `{market_cap_dominance}%`\n\n"
            f"🔝 **Top Companies:**\n\n"
        )

        companies = data.get("companies", [])[:5]  # Fetch top 5 companies
        for company in companies:
            name = company.get("name", "N/A")
            symbol = company.get("symbol", "N/A")
            country = company.get("country", "N/A")
            holdings = company.get("total_holdings", "N/A")
            current_value_usd = company.get("total_current_value_usd", "N/A")
            percentage_supply = company.get("percentage_of_total_supply", "N/A")

            message += (
                f"🏢 **Name**: *{name}* ({symbol})\n"
                f"🌍 **Country**: `{country}`\n"
                f"📈 **Holdings**: `{holdings}`\n"
                f"💰 **Current Value (USD)**: `${current_value_usd:,.2f}`\n"
                f"📉 **% of Total Supply**: `{percentage_supply}%`\n"
                "---------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    url = "https://api.coingecko.com/api/v3/coins/categories?order=market_cap_change_24h_desc"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        top_categories = data[:3]  # Get the first 3 categories
        message = "🏅 **Top 3 Coin Categories (by 24h Market Cap Change)** 🏅\n\n"

        for category in top_categories:
            name = category.get("name", "N/A")
            market_cap = category.get("market_cap", 0)
            market_cap_change = category.get("market_cap_change_24h", 0)
            top_3_coins_id = category.get("top_3_coins_id", [])

            message += (
                f"🌟 **Category Name**: `{name}`\n"
                f"💰 **Market Cap**: `${market_cap:,.2f}`\n"
                f"📉 **24h Market Cap Change**: `{market_cap_change:.2f}%`\n"
                f"🔝 **Top 3 Coins**: `{', '.join(top_3_coins_id) if top_3_coins_id else 'N/A'}`\n"
                "------------------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def coin_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    user_query = " ".join(context.args).strip()
    if not user_query:
        await update.message.reply_text("Please provide a coin name or symbol. Example: `/coin_details btc`", parse_mode="Markdown")
        return

    search_url = f"https://api.coingecko.com/api/v3/search?query={user_query}"
    try:
        search_response = requests.get(search_url)
        search_response.raise_for_status()
        search_data = search_response.json()

        coins_list = search_data.get("coins", [])
        if not coins_list:
            await update.message.reply_text(f"No results found for '{user_query}'. Please try a different query.")
            return

        first_coin = coins_list[0]
        coin_id = first_coin.get("api_symbol", None)
        if not coin_id:
            await update.message.reply_text("Unable to find a valid coin ID. Please try again.")
            return

        await asyncio.sleep(1.5)

        details_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        details_response = requests.get(details_url)
        details_response.raise_for_status()
        details_data = details_response.json()

        name = details_data.get("name")
        symbol = details_data.get("symbol")
        asset_platform_id = details_data.get("asset_platform_id")
        sentiment_votes_up_percentage = details_data.get("sentiment_votes_up_percentage")
        sentiment_votes_down_percentage = details_data.get("sentiment_votes_down_percentage")
        description = details_data.get("description", {}).get("en")
        current_price = details_data.get("market_data", {}).get("current_price", {}).get("usd")
        market_cap = details_data.get("market_data", {}).get("market_cap", {}).get("usd")
        ath = details_data.get("market_data", {}).get("ath", {}).get("usd")
        atl = details_data.get("market_data", {}).get("atl", {}).get("usd")
        price_change_24h = details_data.get("market_data", {}).get("price_change_percentage_24h")

        # Tickers and subfields
        tickers = details_data.get("tickers", [])
        if tickers:
            first_ticker = tickers[0]
            base = first_ticker.get("base")
            target = first_ticker.get("target")
            market_name = first_ticker.get("market", {}).get("name")
            converted_last_usd = first_ticker.get("converted_last", {}).get("usd")
            converted_volume_usd = first_ticker.get("converted_volume", {}).get("usd")
            trust_score = first_ticker.get("trust_score")
            trade_url = first_ticker.get("trade_url")
        else:
            base = target = market_name = converted_last_usd = converted_volume_usd = trust_score = trade_url = None

        message = (
            f"🪙 **Coin Details** 🪙\n\n"
            f"**Name**: `{name} ({symbol.upper()})`\n"
            f"**Platform**: `{asset_platform_id}`\n\n"
            f"💬 **Sentiment Up-vote**: `{sentiment_votes_up_percentage}%`\n"
            f"👎 **Sentiment Down-vote**: `{sentiment_votes_down_percentage}%`\n\n"
            f"📝 **Description**: {description[:200]}...\n\n"
            f"📊 **Market Data** 📊\n"
            f"💵 **Current Price (USD)**: `${current_price:,.4f}`\n"
            f"💰 **Market Cap (USD)**: `${market_cap:,.2f}`\n"
            f"🚀 **All-Time High (USD)**: `${ath:,.8f}`\n"
            f"🏚️ **All-Time Low (USD)**: `${atl:,.8f}`\n"
            f"📉 **24h Price Change**: `{price_change_24h:.4f}%`\n\n"
            f"🏛️ **Best Exchange Information** 🏛️\n"
            f"🏦 **Exchange Name**: `{market_name}`\n"
            f"🌐 **Base - Token Address**: `{base}`\n"
            f"🎯 **Target**: `{target}`\n"
            f"💲 **Last Price (USD)**: `${converted_last_usd:,.8f}`\n"
            f"📈 **Volume (USD)**: `${converted_volume_usd:,.2f}`\n"
            f"⭐ **Trust Score (Exchange)**: `{trust_score}`\n"
            f"🔗 [Swapp Here]({trade_url})\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def bop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /bop <coin> <days>\nExample: /bop btc 1")
        return

    query = context.args[0]
    days = context.args[1]

    if days not in ["1", "7", "14"]:
        await update.message.reply_text("Invalid number of days! Please use 1, 7, or 14.")
        return

    headers = {
        "accept": "application/json",
    }

    encoded_query = urllib.parse.quote(query)

    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={encoded_query}"
        search_response = requests.get(search_url, headers=headers)
        search_response.raise_for_status()
        search_data = search_response.json()


        if search_data.get("coins") and len(search_data["coins"]) > 0:
            first_coin = search_data["coins"][0]
            coin_id = first_coin.get("id")
            name = first_coin.get("name")

            if not coin_id:
                await update.message.reply_text(f"Error: No valid coin ID found for query `{query}`.")
                return
        else:
            await update.message.reply_text(f"No coin found matching the query: {query}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coin information: {e}")
        await update.message.reply_text(f"Error fetching coin information: {e}")
        return

    await asyncio.sleep(2)

    try:
        ohlc_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc?vs_currency=usd&days={days}"

        ohlc_response = requests.get(ohlc_url, headers=headers)
        ohlc_response.raise_for_status()
        ohlc_data = ohlc_response.json()


        if not ohlc_data:
            await update.message.reply_text(f"No OHLC data found for {name} in the last {days} days.")
            return
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Error fetching OHLC data: {e}")
        return

    try:
        daily_bop = defaultdict(list)

        for entry in ohlc_data:
            timestamp, open_price, high_price, low_price, close_price = entry
            date = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')

            if high_price != low_price:
                bop = (close_price - open_price) / (high_price - low_price)
                daily_bop[date].append(bop)

        aggregated_bop = {date: sum(values) / len(values) for date, values in daily_bop.items()}

        if not aggregated_bop:
            await update.message.reply_text(f"No valid BOP data found for {name}.")
            return

        message = f"📊 **Aggregated Balance of Power (BOP) for {name} ({days}-day OHLC):**\n\n"
        for date, avg_bop in sorted(aggregated_bop.items()):
            pressure = "🔼 Buy Pressure" if avg_bop > 0 else "🔽 Sell Pressure"
            message += f"📅 **{date}**: `{avg_bop:.4f}` ({pressure})\n"

        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception as e:
        # Catch any unexpected errors during calculation
        print(f"Unexpected error during BOP calculation: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")




def main():
    TELEGRAM_API_KEY = os.getenv("telegram_api_token")
    application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("trending", trending))
    application.add_handler(CommandHandler("dominance", dominance))
    application.add_handler(CommandHandler("companies", companies))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("coin_details", coin_details))
    application.add_handler(CommandHandler("bop", bop))

    application.run_polling()


if __name__ == "__main__":
    main()
