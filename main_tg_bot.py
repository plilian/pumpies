# Copyright 2024 plilian
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
        "👋 **Welcome to Coin Lens!**\n\n"
        "I'm here to help you stay updated with the latest cryptocurrency data. "
        "Use the following commands to interact with me:\n\n"

        "💡 **Examples:**\n"
        "   `/search bitcoin`\n"
        "   `/trending`\n"
        "   `/dominance`\n"
        "   `/companies ethereum or /companies bitcoin`\n"
        "   `/categories`\n"
        "   `/coin_details_name btc`\n"
        "   `/coin_details_address solana/ethereum ca`\n"
        "   `/rsi btc 1d, 2d.. to 14d`\n"
        "   `/bop btc 1 or 7 or 14 (days)`\n"
        "   `/top_boosted_tokens`\n"
        "   `/latest_boosted_tokens `\n"
        "   `/trade_info ca `\n"
        "   `/token_orders ethereum/solana ca`\n\n"

        "If you have any questions or need further assistance, feel free to reach out! ☺️"
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
            "Please specify a coin ID (bitcoin or ethereum). Usage: /companies <coin_id>"
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


async def coin_details_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    user_query = " ".join(context.args).strip()
    if not user_query:
        await update.message.reply_text("Please provide a coin name or symbol. Example: `/coin_details_name btc`", parse_mode="Markdown")
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
        watchlist_portfolio_users = details_data.get("watchlist_portfolio_users")
        total_supply = details_data.get("market_data", {}).get("total_supply", {})
        max_supply = details_data.get("market_data", {}).get("max_supply", {})
        circulating_supply = details_data.get("market_data", {}).get("circulating_supply", {})
        description = details_data.get("description", {}).get("en")
        current_price = details_data.get("market_data", {}).get("current_price", {}).get("usd")
        market_cap = details_data.get("market_data", {}).get("market_cap", {}).get("usd")
        ath = details_data.get("market_data", {}).get("ath", {}).get("usd")
        atl = details_data.get("market_data", {}).get("atl", {}).get("usd")
        price_change_24h = details_data.get("market_data", {}).get("price_change_percentage_24h")


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
            f"👍 **Sentiment Up-vote**: `{sentiment_votes_up_percentage}%`\n"
            f"👎 **Sentiment Down-vote**: `{sentiment_votes_down_percentage}%`\n"
            f"💬 **Watch List Users**: `{watchlist_portfolio_users}`\n\n"
            f"📝 **Description**: {description[:200]}...\n\n"
            f"📊 **Market Data** 📊\n\n"
            f"💵 **Current Price (USD)**: `${current_price:,.4f}`\n"
            f"ℹ️ **Total Supply (#)**: `{total_supply}`\n"
            f"ℹ️ **Max Supply (#)**: `{max_supply}`\n"
            f"ℹ️ **Circulating Supply (#)**: `{circulating_supply}`\n"
            f"💰 **Market Cap (USD)**: `${market_cap:,.2f}`\n"
            f"🚀 **All-Time High (USD)**: `${ath:,.8f}`\n"
            f"🏚️ **All-Time Low (USD)**: `${atl:,.8f}`\n"
            f"📉 **24h Price Change**: `{price_change_24h:.4f}%`\n\n"
            f"🏛️ **Top Exchange Information** 🏛️\n\n"
            f"🏦 **Exchange Name**: `{market_name}`\n"
            f"🌐 **Base - Token Address**: `{base}`\n"
            f"🎯 **Target**: `{target}`\n"
            f"💲 **Last Price (USD)**: `${converted_last_usd:,.8f}`\n"
            f"📈 **Volume (USD)**: `${converted_volume_usd:,.2f}`\n"
            f"⭐ **Trust Score (Exchange)**: `{trust_score}`\n\n"
            f"🔗 [Swapp Here]({trade_url})\n"
        )

        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def coin_details_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    user_query = " ".join(context.args).strip()
    if not user_query:
        await update.message.reply_text(
            "Please provide the platform (ethereum/solana) and the contract address.\n"
            "Example: `/coin_details_address ethereum 0x1234567890abcdef...`",
            parse_mode="Markdown",
        )
        return

    query_parts = user_query.split()
    if len(query_parts) < 2:
        await update.message.reply_text(
            "Invalid format. Use: `/coin_details_address platform contract_address`.\n"
            "Example: `/coin_details_address ethereum 0x1234567890abcdef...`",
            parse_mode="Markdown",
        )
        return

    platform = query_parts[0].lower()
    contract_address = query_parts[1]

    if platform not in ["ethereum", "solana"]:
        await update.message.reply_text(
            "Invalid platform. Only `ethereum` and `solana` are supported.",
            parse_mode="Markdown",
        )
        return

    details_url = f"https://api.coingecko.com/api/v3/coins/{platform}/contract/{contract_address}"

    try:
        details_response = requests.get(details_url)
        details_response.raise_for_status()
        details_data = details_response.json()


        name = details_data.get("name")
        symbol = details_data.get("symbol")
        asset_platform_id = details_data.get("asset_platform_id")
        sentiment_votes_up_percentage = details_data.get("sentiment_votes_up_percentage")
        sentiment_votes_down_percentage = details_data.get("sentiment_votes_down_percentage")
        watchlist_portfolio_users = details_data.get("watchlist_portfolio_users")
        total_supply = details_data.get("market_data", {}).get("total_supply", {})
        max_supply = details_data.get("market_data", {}).get("max_supply", {})
        circulating_supply = details_data.get("market_data", {}).get("circulating_supply", {})
        description = details_data.get("description", {}).get("en")
        current_price = details_data.get("market_data", {}).get("current_price", {}).get("usd")
        market_cap = details_data.get("market_data", {}).get("market_cap", {}).get("usd")
        ath = details_data.get("market_data", {}).get("ath", {}).get("usd")
        atl = details_data.get("market_data", {}).get("atl", {}).get("usd")
        price_change_24h = details_data.get("market_data", {}).get("price_change_percentage_24h")

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
            f"👍 **Sentiment Up-vote**: `{sentiment_votes_up_percentage}%`\n"
            f"👎 **Sentiment Down-vote**: `{sentiment_votes_down_percentage}%`\n"
            f"💬 **Watch List Users**: `{watchlist_portfolio_users}`\n\n"
            f"📝 **Description**: {description[:200]}...\n\n"
            f"📊 **Market Data** 📊\n\n"
            f"💵 **Current Price (USD)**: `${current_price:,.4f}`\n"
            f"ℹ️ **Total Supply (#)**: `{total_supply}`\n"
            f"ℹ️ **Max Supply (#)**: `{max_supply}`\n"
            f"ℹ️ **Circulating Supply (#)**: `{circulating_supply}`\n"
            f"💰 **Market Cap (USD)**: `${market_cap:,.2f}`\n"
            f"🚀 **All-Time High (USD)**: `${ath:,.8f}`\n"
            f"🏚️ **All-Time Low (USD)**: `${atl:,.8f}`\n"
            f"📉 **24h Price Change**: `{price_change_24h:.4f}%`\n\n"
            f"🏛️ **Top Exchange Information** 🏛️\n\n"
            f"🏦 **Exchange Name**: `{market_name}`\n"
            f"🌐 **Base - Token Address**: `{base}`\n"
            f"🎯 **Target**: `{target}`\n"
            f"💲 **Last Price (USD)**: `${converted_last_usd:,.8f}`\n"
            f"📈 **Volume (USD)**: `${converted_volume_usd:,.2f}`\n"
            f"⭐ **Trust Score (Exchange)**: `{trust_score}`\n\n"
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
        print(f"Unexpected error during BOP calculation: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")


async def rsi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    user_query = " ".join(context.args).strip()
    if not user_query:
        await update.message.reply_text("Please provide a coin name or symbol. Example: `/rsi btc 1h`", parse_mode="Markdown")
        return

    query_parts = user_query.split()
    coin_symbol = query_parts[0]
    time_period = query_parts[1] if len(query_parts) > 1 else "1d"
    interval_choice = query_parts[2] if len(query_parts) > 2 else None

    if time_period.endswith('d'):
        days = int(time_period[:-1])
        if days < 1 or days > 14:
            await update.message.reply_text("The allowed range for days is between 1 and 14. Please adjust your input.")
            return
        interval = 'daily'
    else:
        days = 1
        interval = 'daily'

    search_url = f"https://api.coingecko.com/api/v3/search?query={coin_symbol}"
    try:
        search_response = requests.get(search_url)
        search_response.raise_for_status()
        search_data = search_response.json()

        coins_list = search_data.get("coins", [])
        if not coins_list:
            await update.message.reply_text(f"No results found for '{coin_symbol}'. Please try a different query.")
            return

        first_coin = coins_list[0]
        coin_id = first_coin.get("id", None)

        if not coin_id:
            await update.message.reply_text("Unable to find a valid coin ID. Please try again.")
            return

        await asyncio.sleep(1.5)
        cg_api_key = os.getenv("CG_API_KEY")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval={interval}"

        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": cg_api_key
        }

        chart_response = requests.get(url, headers=headers)
        chart_response.raise_for_status()
        chart_data = chart_response.json()

        prices = chart_data.get('prices', [])
        if not prices:
            await update.message.reply_text(f"No price data available for {coin_symbol}. Please try again later.")
            return

        closing_prices = [price[1] for price in prices]

        total_rsi = calculate_rsi(closing_prices, period=len(closing_prices))

        total_rsi_interpretation = interpret_rsi(total_rsi)

        await update.message.reply_text(
            f"📉 **Relative Strength Index (RSI)** for *{coin_symbol.upper()}* (Last {days} days):\n\n"
            f"🔸 **RSI**: *{total_rsi:.2f}* - {total_rsi_interpretation}\n\n"
            f"*Note: RSI is a momentum indicator used to assess whether an asset is overbought (>70) or oversold (<30).*\n\n"
            f"🔄 *RSI between 30 and 70 suggests neutral market conditions.*"
        )

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")

def calculate_rsi(prices, period=14):
    gains = []
    losses = []

    for i in range(1, len(prices)):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(prices)):
        gain = gains[i]
        loss = losses[i]

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return rsi

def interpret_rsi(rsi):
    if rsi > 70:
        return "Overbought - The asset might be overvalued and could be due for a correction."
    elif rsi < 30:
        return "Oversold - The asset might be undervalued and could be due for an increase."
    else:
        return "Neutral - The asset is in a balanced state."


async def top_boosted_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    url = "https://api.dexscreener.com/token-boosts/top/v1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        top_tokens = data[:5]  # Get the first 5 tokens
        message = "🔥 **Top 5 Boosted Tokens** 🔥\n\n"

        for token in top_tokens:
            token_address = token.get("tokenAddress", "N/A")
            platform = token.get("chainId", "N/A")
            description = token.get("description", "No description available")
            url = token.get("url", "N/A")
            links = token.get("links", [])

            # Build the links section
            links_message = ""
            for link in links:
                link_type = link.get("type", link.get("label", "Unknown"))
                link_url = link.get("url", "N/A")
                links_message += f"  - **{link_type.capitalize()}**: [Link]({link_url})\n"

            message += (
                f"🔗 **DexScreener URL**: [Link]({url})\n"
                f"🌐 **Platform**: `{platform}`\n\n"
                f"🏷️ **Token Address**: `{token_address}`\n\n"
                f"📝 **Description**: {description}\n\n"
                f"🔗 **Links**:\n{links_message}\n"
                "------------------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")

async def latest_boosted_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    url = "https://api.dexscreener.com/token-boosts/top/v1"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        top_tokens = data[:5]
        message = "🔥 **Latest Boosted Tokens** 🔥\n\n"

        for token in top_tokens:
            token_address = token.get("tokenAddress", "N/A")
            platform = token.get("chainId", "N/A")
            description = token.get("description", "No description available")
            url = token.get("url", "N/A")
            links = token.get("links", [])

            # Build the links section
            links_message = ""
            for link in links:
                link_type = link.get("type", link.get("label", "Unknown"))
                link_url = link.get("url", "N/A")
                links_message += f"  - **{link_type.capitalize()}**: [Link]({link_url})\n"

            message += (
                f"🔗 **DexScreener URL**: [Link]({url})\n"
                f"🌐 **Platform**: `{platform}`\n\n"
                f"🏷️ **Token Address**: `{token_address}`\n\n"
                f"📝 **Description**: {description}\n\n"
                f"🔗 **Links**:\n{links_message}\n"
                "------------------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


async def token_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide the chain ID and token address. Example: `/token_orders ethereum 0x...`",
            parse_mode="Markdown"
        )
        return

    chain_id = context.args[0].lower()
    token_address = context.args[1]

    if chain_id not in ["ethereum", "solana"]:
        await update.message.reply_text("Invalid chain ID. Please use either `ethereum` or `solana`.", parse_mode="Markdown")
        return

    url = f"https://api.dexscreener.com/orders/v1/{chain_id}/{token_address}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            await update.message.reply_text("No orders found for the specified token.")
            return

        message = f"📋 **Orders for Token**\n🌐 **Chain**: `{chain_id}`\n🏷️ **Token Address**: `{token_address}`\n\n"

        type_mapping = {
            "tokenProfile": "Profile added to Dex Screener",
            "communityTakeover": "Takeover by the Community",
            "tokenAd": "Ads in Dex Screener",
            "trendingBarAd": "Ads in Trending Bar in Dex Screener"
        }

        for order in data:
            order_type = order.get("type", "Unknown")
            status = order.get("status", "Unknown")
            timestamp = order.get("paymentTimestamp", 0)
            datetime_str = datetime.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")

            message += (
                f"🔹 **Type**: `{type_mapping.get(order_type, order_type)}`\n"
                f"🔹 **Status**: `{status.capitalize()}`\n"
                f"🔹 **Date/Time**: `{datetime_str}`\n"
                "------------------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")



async def trade_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_rate_limit(update):
        await update.message.reply_text("You're sending commands too quickly. Please wait a second and try again.")
        return

    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: `/trade_info tokenAddress`",
            parse_mode="Markdown"
        )
        return

    token_address = context.args[0]
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        pairs = data.get("pairs", [])

        if not pairs:
            await update.message.reply_text("No data found for the given token address. Please try again.")
            return

        message = f"📊 **Token Info for {token_address}** 📊\n\n"

        for pair in pairs:
            dex_id = pair.get("dexId", "N/A")
            dex_url = pair.get("url", "N/A")
            pair_address = pair.get("pairAddress", "N/A")
            base_symbol = pair.get("baseToken", {}).get("symbol", "N/A")
            quote_symbol = pair.get("quoteToken", {}).get("symbol", "N/A")
            price_native = pair.get("priceNative", "N/A")
            price_usd = pair.get("priceUsd", "N/A")
            transactions = pair.get("txns", {})
            volume = pair.get("volume", {})
            price_change = pair.get("priceChange", {})
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            market_cap = pair.get("marketCap", "N/A")
            fdv = pair.get("fdv", "N/A")
            active_boosts = pair.get("boosts", {}).get("active", "N/A")

            txns_message = "\n".join(
                [
                    f"🕒 `{key}`: Buys: `{value.get('buys', 0)}`, Sells: `{value.get('sells', 0)}`"
                    for key, value in transactions.items()
                ]
            )

            volume_message = "\n".join(
                [f"🕒 `{key}`: `${value:,.2f}`" for key, value in volume.items()]
            )

            price_change_message = "\n".join(
                [f"🕒 `{key}`: `{value:.2f}%`" for key, value in price_change.items()]
            )

            message += (
                f"🌐 **DEX**: `{dex_id}`\n"
                f"🔗 [DEX Screener URL]({dex_url})\n"
                f"🏷️ **Pair Address**: `{pair_address}`\n"
                f"🔄 **Base - Quote**: `{base_symbol} / {quote_symbol}`\n"
                f"💵 **Price (Native)**: `{price_native}`\n"
                f"💲 **Price (USD)**: `{price_usd}`\n\n"
                f"📈 **Transactions:**\n{txns_message}\n\n"
                f"📊 **Volume (USD):**\n{volume_message}\n\n"
                f"📉 **Price Change (%):**\n{price_change_message}\n\n"
                f"💧 **Liquidity (USD)**: `${liquidity:,.2f}`\n"
                f"🏦 **Market Cap**: `${market_cap}`\n"
                f"🔮 **FDV**: `${fdv}`\n"
                f"🔥 **Active Boosts**: `{active_boosts}`\n"
                "------------------------------------\n"
            )

        await update.message.reply_text(message, parse_mode="Markdown", disable_web_page_preview=False)

    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"An error occurred while fetching data: {e}")


def main():
    TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
    application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("trending", trending))
    application.add_handler(CommandHandler("dominance", dominance))
    application.add_handler(CommandHandler("companies", companies))
    application.add_handler(CommandHandler("categories", categories))
    application.add_handler(CommandHandler("coin_details_name", coin_details_name))
    application.add_handler(CommandHandler("bop", bop))
    application.add_handler(CommandHandler("rsi", rsi))
    application.add_handler(CommandHandler("coin_details_address", coin_details_address))
    application.add_handler(CommandHandler("top_boosted_tokens", top_boosted_tokens))
    application.add_handler(CommandHandler("latest_boosted_tokens", latest_boosted_tokens))
    application.add_handler(CommandHandler("token_orders", token_orders))
    application.add_handler(CommandHandler("trade_info", trade_info))


    application.run_polling()


if __name__ == "__main__":
    main()
