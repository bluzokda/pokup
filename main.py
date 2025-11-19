import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN, ARBITRAGE_THRESHOLD
from scraper import get_funpay_items
from playerok_api import get_playerok_items
from matcher import find_best_match
from db import log_deal, init_db, get_stats

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

monitoring_active = False

# Глобальный словарь для отслеживания активных мониторингов (если нужно для нескольких пользователей)
active_monitors = {}

# Клавиатура с кнопками
def get_main_keyboard():
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🟢 Начать мониторинг", callback_data="start_monitoring"),
        ],
        [
            types.InlineKeyboardButton(text="🔴 Остановить мониторинг", callback_data="stop_monitoring"),
        ],
        [
            types.InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        ]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска арбитража между FunPay и PlayerOK.\n"
        "Используй кнопки ниже для управления.",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer(
        "Меню управления:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "start_monitoring")
async def cb_start_monitoring(callback_query: types.CallbackQuery):
    global monitoring_active
    user_id = callback_query.from_user.id

    if user_id in active_monitors and active_monitors[user_id]:
        await callback_query.answer("Мониторинг уже запущен!", show_alert=True)
        return

    active_monitors[user_id] = True
    await callback_query.answer("Мониторинг запущен!")
    await bot.send_message(user_id, "🟢 Мониторинг запущен...")
    asyncio.create_task(monitor_loop(user_id))

@dp.callback_query(lambda c: c.data == "stop_monitoring")
async def cb_stop_monitoring(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if active_monitors.get(user_id):
        active_monitors[user_id] = False
        await callback_query.answer("Мониторинг остановлен!")
        await bot.send_message(user_id, "🔴 Мониторинг остановлен.")
    else:
        await callback_query.answer("Мониторинг не запущен!", show_alert=True)

@dp.callback_query(lambda c: c.data == "stats")
async def cb_stats(callback_query: types.CallbackQuery):
    stats = get_stats()
    total_deals, total_profit = stats
    await callback_query.answer(
        f"📊 Статистика:\n"
        f"Всего сделок: {total_deals}\n"
        f"Общая прибыль: {total_profit:.2f}₽",
        show_alert=True
    )

async def monitor_loop(user_id):
    while active_monitors.get(user_id, False):
        fp_items = get_funpay_items()
        for fp_item in fp_items:
            po_items = get_playerok_items(fp_item["name"])
            po_item = find_best_match(fp_item, po_items)
            if po_item:
                profit = po_item["price"] - fp_item["price"]
                if profit > ARBITRAGE_THRESHOLD:
                    await bot.send_message(
                        user_id,
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
