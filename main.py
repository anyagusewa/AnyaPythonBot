import telebot
import requests
from bs4 import BeautifulSoup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Получаем токен из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)


# Функции для получения курса монеты с разных бирж

def get_price_bybit(symbol):
    url = "https://api.bybit.com/v5/market/tickers"
    params = {"category": "spot", "symbol": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["result"]["list"][0]["lastPrice"]
    else:
        return f"Ошибка: {response.text}"


def get_price_binance(symbol):
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["price"]
    else:
        return f"Ошибка: {response.text}"


def get_price_mexc(symbol):
    url = "https://api.mexc.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["price"]
    else:
        return f"Ошибка: {response.text}"


def get_price_okx(symbol):
    url = "https://www.okx.com/api/v5/market/ticker"
    params = {"instId": symbol.replace("USDT", "-USDT")}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["data"][0]["last"]
    else:
        return f"Ошибка: {response.text}"


# Функция для получения топ-10 трендовых монет с CoinMarketCap
def get_top_10_coins():
    url = "https://coinmarketcap.com/ru/trending-cryptocurrencies"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    coins = soup.find_all('p', class_="sc-71024e3e-0 ehyBa-d")[:10]  # Находим топ-10 монет

    top_10_list = ""
    n = 1
    for coin in coins:
        top_10_list += f"{n}. {coin.text}\n"
        n += 1

    return top_10_list if top_10_list else "Не удалось получить данные о монетах."

# Функция для получения топ-10 монет по рыночной капитализации с CoinMarketCap
def get_top_10_coins_cap():
    url = "https://coinmarketcap.com/ru/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    coins = soup.find_all('p', class_="sc-65e7f566-0 iPbTJf coin-item-name")[:10]  # Находим топ-10 монет

    top_10_list = ""
    n = 1
    for coin in coins:
        top_10_list += f"{n}. {coin.text}\n"
        n += 1

    return top_10_list if top_10_list else "Не удалось получить данные о монетах."


# Функция для получения новостей
def get_news():
    url = "https://www.rbc.ru/crypto/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Ищем заголовки и ссылки
    headlines = soup.find_all("span", class_="normal-wrap")
    links = soup.find_all("a", class_="item__link")

    # Список для хранения заголовков и ссылок
    news_list = []

    for headline, link in zip(headlines, links):
        news_list.append({
            "title": headline.text.strip(),
            "url": link.get("href")
        })

    # возвращаем список словарей
    return news_list



# Выбор действия
@bot.message_handler(commands=["start"])
def start_message(message):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_price = InlineKeyboardButton("📈 Узнать курс монеты", callback_data="action_price")
    btn_top10 = InlineKeyboardButton("🔥 Топ-10 трендовых монет", callback_data="action_top10")
    btn_top10_cap = InlineKeyboardButton("💰 Топ-10 монет по рыночной капитализации", callback_data="action_top10cap")
    btn_news = InlineKeyboardButton("📰 Свежие новости мира криптовалюты", callback_data="action_news")
    markup.add(btn_price, btn_top10, btn_top10_cap, btn_news)

    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


# Обработка выбора действия
@bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
def handle_action(call):
    action = call.data.split("_")[1]

    if action == "price":
        choose_coin(call.message)  # Переход к выбору монеты
    elif action == "top10":
        top_10_coins = get_top_10_coins()
        bot.send_message(call.message.chat.id, f"🔥 Топ-10 трендовых монет:\n{top_10_coins}")
    elif action == "top10cap":
        top_10_coins_cap = get_top_10_coins_cap()
        bot.send_message(call.message.chat.id, f"💰 Топ-10 монет по рыночной капитализации:\n{top_10_coins_cap}")
    elif action == "news":
        top_news = get_news()
        news_message = "📰 Свежие новости мира криптовалюты:\n\n"
        for news in top_news:
            news_message += f" {news['title']}\n🔗 {news['url']}\n\n"
        bot.send_message(call.message.chat.id, news_message)

# Выбор монеты
def choose_coin(message):
    markup = InlineKeyboardMarkup(row_width=1)
    btn_btc = InlineKeyboardButton("Bitcoin (BTC)", callback_data="coin_BTCUSDT")
    btn_eth = InlineKeyboardButton("Ethereum (ETH)", callback_data="coin_ETHUSDT")
    btn_sol = InlineKeyboardButton("Solana (SOL)", callback_data="coin_SOLUSDT")
    markup.add(btn_btc, btn_eth, btn_sol)

    bot.send_message(message.chat.id, "Выберите монету:", reply_markup=markup)


# Выбор биржи
@bot.callback_query_handler(func=lambda call: call.data.startswith("coin_"))
def choose_exchange(call):
    coin = call.data.split("_")[1]

    markup = InlineKeyboardMarkup(row_width=2)
    btn_bybit = InlineKeyboardButton("Bybit", callback_data=f"exchange_bybit_{coin}")
    btn_binance = InlineKeyboardButton("Binance", callback_data=f"exchange_binance_{coin}")
    btn_mexc = InlineKeyboardButton("Mexc", callback_data=f"exchange_mexc_{coin}")
    btn_okx = InlineKeyboardButton("Okx", callback_data=f"exchange_okx_{coin}")

    markup.add(btn_bybit, btn_binance, btn_mexc, btn_okx)

    bot.send_message(call.message.chat.id, "Выберите биржу:", reply_markup=markup)


# Получение курса
@bot.callback_query_handler(func=lambda call: call.data.startswith("exchange_"))
def get_price(call):
    _, exchange, coin = call.data.split("_")

    if exchange == "bybit":
        price = get_price_bybit(coin)
    elif exchange == "binance":
        price = get_price_binance(coin)
    elif exchange == "mexc":
        price = get_price_mexc(coin)
    elif exchange == "okx":
        price = get_price_okx(coin)
    else:
        price = "Ошибка: Биржа не найдена"

    bot.send_message(call.message.chat.id, f"Курс {coin[:-4]}/USDT на {exchange.capitalize()}: {price} USDT")


# Запуск бота
bot.polling(none_stop=True)


