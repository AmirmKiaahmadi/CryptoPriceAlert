import requests
import schedule
import time
import asyncio
from telegram import Bot
import requests
from bs4 import BeautifulSoup

TELEGRAM_BOT_TOKEN = "7795207277:AAE1UwkVqpjHpLt4Dn7jzYyh-Op2iZ1NeTY"
TELEGRAM_CHANNEL_ID = "-1002373778351"

bot = Bot(token=TELEGRAM_BOT_TOKEN)


# Fetch crypto prices from CoinGecko
def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=bitcoin,ethereum"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

#nobitex scrapper
def get_tether_price():
    url = "https://nobitex.ir/prices/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table" , class_="flex w-full max-w-full flex-col items-center overflow-x-auto flex desktop:hidden")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                if "USDT" in row.text:
                    irt_span = row.find("span", class_="text-txt-neutral-default")
                    if irt_span:
                        return irt_span.text.strip().upper()
    return None




# Send CoinGecko prices to Telegram
async def send_crypto_prices_to_telegram():
    crypto_data = get_crypto_prices()
    if crypto_data:
        message = "📊 *آخرین قیمت‌های ارزهای دیجیتال*\n\n"  # Initialize message with a header
        for coin in crypto_data:
            name = coin["name"]
            price = coin["current_price"]
            percent = round(coin["price_change_percentage_24h"], 2)
            movement = "رشد" if percent > 0 else "کاهش"
            message += (
                f"⚡️ {name}\n"
                f"قیمت: ${price:,}\n"
                f"تغییرات ۲۴ ساعت: {abs(percent)}% {movement}\n\n"
            )
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=False,
            )
        except Exception as e:
            print("Failed to send message:")

# Send Tether price to Telegram
async def send_tether_price_to_telegram():
    tether_price = get_tether_price()
    if tether_price:
        image_url = "https://assets.coingecko.com/coins/images/325/large/Tether-logo.png?1598003707"
        message = (
            f"📊 *آخرین قیمت تتر*\n\n💰 {tether_price} تومان"
            # f"[ ]({image_url})\n\n"
        )
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message,
                parse_mode="Markdown",
            )
        except Exception as e:
            print("Failed to send Tether price:")


# Wrapper functions for scheduling
def job_wrapper_crypto():
    asyncio.run(send_crypto_prices_to_telegram())


def job_wrapper_tether():
    asyncio.run(send_tether_price_to_telegram())


# Schedule tasks
schedule.every(8).hours.do(job_wrapper_crypto)  # Crypto prices every 1 hour
schedule.every(8).hours.do(job_wrapper_tether)  # Tether price every 8 hours

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
