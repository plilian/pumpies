## License

Copyright 2024 plilian  
Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at  

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)  

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.  



# Coin Lens Telegram Bot

Coin Lens is a feature-rich Telegram bot that provides real-time cryptocurrency data, insights, and tools for enthusiasts, traders, and researchers. With easy-to-use commands, users can fetch details about cryptocurrencies, market trends, trading insights, and much more.

## Features

- **Search**: Quickly look up coins and fetch details like name, symbol, and market cap rank.
- **Trending Coins**: Stay updated with the latest trending cryptocurrencies.
- **Market Dominance**: View dominance data for major cryptocurrencies like Bitcoin and Ethereum.
- **Crypto Categories**: Discover the top-performing cryptocurrency categories based on 24-hour market cap changes.
- **Coin Details**: Fetch detailed information about coins using their name or address.
- **Technical Analysis Tools**: Calculate RSI and Buy/Sell Pressure (BOP) over various timeframes.
- **Token Orders**: Retrieve token orders on Ethereum and Solana chains.
- **Trading Information**: View trading details of tokens, including transactions, volume, price changes, and liquidity.
- **Boosted Tokens**: Fetch the top and latest boosted tokens.

## Commands

| Command                  | Description                                                                                  | Example                                 |
|--------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------|
| `/start`                 | Start interacting with the bot and get a welcome message.                                   |                                         |
| `/search`                | Search for a coin and get its basic details like name, symbol, and market cap rank.          | `/search bitcoin`                       |
| `/trending`              | Get a list of trending cryptocurrencies based on their market performance.                  |                                         |
| `/dominance`             | Get the market dominance of major cryptocurrencies like Bitcoin and Ethereum.               |                                         |
| `/companies`             | Fetch information about top crypto companies or projects.                                   | `/companies ethereum`                   |
| `/categories`            | Display the top 3 cryptocurrency categories based on 24-hour market cap change.             |                                         |
| `/coin_details_name`     | Fetch detailed information about a coin using its name.                                     | `/coin_details_name btc`                |
| `/coin_details_address`  | Fetch detailed information about a coin using its address.                                  | `/coin_details_address ethereum ca`     |
| `/rsi`                   | Calculate the RSI of a cryptocurrency over the past 14 days.                                | `/rsi btc 1d`                           |
| `/bop`                   | Calculate the Buy/Sell Pressure (BOP) of a cryptocurrency over the past 1, 7, or 14 days.   | `/bop btc 7`                            |
| `/top_boosted_tokens`    | View the top boosted tokens in the market.                                                  |                                         |
| `/latest_boosted_tokens` | Get the latest boosted tokens in the market.                                                |                                         |
| `/trade_info`            | Fetch trading details of a token, including price, volume, and transactions.                | `/trade_info ca`                        |
| `/token_orders`          | Fetch token order details for Ethereum or Solana.                                           | `/token_orders solana ca`               |

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/plilian/coin_lens_tg_bot.git
   cd coin_lens_tg_bot
