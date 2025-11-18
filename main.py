import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ARBITRAGE_THRESHOLD
from scraper import get_funpay_items
from playerok_api import get_playerok_items
from matcher import find_best_match
from db import log_deal, init_db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

monitoring_active = False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска арбитража между FunPay и PlayerOK.\n"
        "Используй /start_monitoring и /stop_monitoring для управления."
    )

@dp.message(Command("start_monitoring"))
async def cmd_start_monitoring(message: types.Message):
    global monitoring_active
    if monitoring_active:
        await message.answer("Мониторинг уже запущен.")
        return
    monitoring_active = True
    await message.answer("Мониторинг запущен...")
    asyncio.create_task(monitor_loop(chat_id=message.chat.id))

@dp.message(Command("stop_monitoring"))
async def cmd_stop_monitoring(message: types.Message):
    global monitoring_active
    monitoring_active = False
    await message.answer("Мониторинг остановлен.")

async def monitor_loop(chat_id):
    while monitoring_active:
        fp_items = get_funpay_items()
        for fp_item in fp_items:
            po_items = get_playerok_items(fp_item["name"])
            po_item = find_best_match(fp_item, po_items)
            if po_item:
                profit = po_item["price"] - fp_item["price"]
                if profit > ARBITRAGE_THRESHOLD:
                    await bot.send_message(
                        chat_id,
                        f"🔍 Найдена арбитражная сделка:\n"
                        f"🛒 Купить на FunPay: {fp_item['name']} за {fp_item['price']}₽\n"
                        f"💰 Продать на PlayerOK: за {po_item['price']}₽\n"
                        f"📈 Прибыль: {profit:.2f}₽\n"
                        f"🔗 Ссылки:\n- FunPay: [ссылка]\n- PlayerOK: [ссылка]"
                    )
                    log_deal(fp_item["name"], fp_item["price"], po_item["price"], profit)
        await asyncio.sleep(60)  # Пауза между проверками

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
