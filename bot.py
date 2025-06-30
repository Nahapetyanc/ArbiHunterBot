import os

import asyncio

from dotenv import load_dotenv

import ccxt.async_support as ccxt

from aiogram import Bot, Dispatcher, types



load_dotenv()  # Загружаем переменные из .env


print(f"Используем токен: {TOKEN[:5]}...{TOKEN[-5:]}")

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:

    print("❌ Ошибка: BOT_TOKEN не найден в переменных окружения")

    exit(1)



bot = Bot(token=TOKEN)

dp = Dispatcher(bot)



@dp.message()

async def echo_all(message: types.Message):

    await message.answer("Привет! Я на связи!")


async def check_prices():

    exchanges = {

        "binance": ccxt.binance({"enableRateLimit": True}),

        "bybit": ccxt.bybit({"enableRateLimit": True}),

    }

    await asyncio.gather(*(ex.load_markets() for ex in exchanges.values()))

    print("✅ Биржи загружены, начинаем мониторинг...")



    while True:

        try:

            for symbol in ["BTC/USDT", "ETH/USDT"]:

                prices = {}

                for name, ex in exchanges.items():

                    ticker = await ex.fetch_ticker(symbol)

                    prices[name] = ticker['last']

                diff = (prices['bybit'] / prices['binance'] - 1) * 100

                if abs(diff) >= 3:

                    msg = (f"🎯 {symbol} | Binance: {prices['binance']:.2f}, "

                           f"Bybit: {prices['bybit']:.2f} | Разница: {diff:.2f}%")

                    # Заменить chat_id на свой Telegram ID или куда присылать

                    await bot.send_message(chat_id=TOKEN.split(':')[0], text=msg)

            await asyncio.sleep(15)

        except Exception as e:

            print(f"Ошибка в цикле проверки цен: {e}")

            await asyncio.sleep(10)



async def main():

    print("🚀 Запуск бота...")

    await dp.start_polling()



if __name__ == "__main__":

    loop = asyncio.get_event_loop()

    loop.create_task(check_prices())

    loop.run_until_complete(main())