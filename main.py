import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import TELEGRAM_BOT_TOKEN, ARBITRAGE_THRESHOLD
from scraper import get_funpay_items
from playerok_api import get_playerok_items
from matcher import find_best_match
from db import log_deal, init_db, get_stats

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Глобальные переменные
monitoring_active = {}
user_categories = {}  # {user_id: category}

# Категории
CATEGORIES = {
    "cs2": "CS2",
    "dota2": "Dota 2",
    "rust": "Rust",
    "csgo": "CS:GO",
    "roblox": "Roblox"
}

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
        ],
        [
            types.InlineKeyboardButton(text="🎮 Выбрать категорию", callback_data="select_category"),
        ]
    ])
    return keyboard

def get_category_keyboard():
    buttons = []
    for key, name in CATEGORIES.items():
        buttons.append([types.InlineKeyboardButton(text=name, callback_data=f"category_{key}")])
    buttons.append([types.InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_category")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для поиска арбитража между FunPay и PlayerOK.\n"
        "Используй кнопки ниже для управления.",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "start_monitoring")
async def cb_start_monitoring(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in user_categories:
        await callback_query.answer("Сначала выбери категорию!", show_alert=True)
        return

    if user_id in monitoring_active and monitoring_active[user_id]:
        await callback_query.answer("Мониторинг уже запущен!", show_alert=True)
        return

    monitoring_active[user_id] = True
    await callback_query.answer("Мониторинг запущен!")
    await bot.send_message(user_id, f"🟢 Мониторинг запущен для категории: {CATEGORIES[user_categories[user_id]]}")
    asyncio.create_task(monitor_loop(user_id))

@dp.callback_query(lambda c: c.data == "stop_monitoring")
async def cb_stop_monitoring(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if monitoring_active.get(user_id):
        monitoring_active[user_id] = False
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

@dp.callback_query(lambda c: c.data == "select_category")
async def cb_select_category(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Выбери категорию:",
        reply_markup=get_category_keyboard()
    )

@dp.callback_query(lambda c: c.data.startswith("category_"))
async def cb_category_selected(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    category_key = callback_query.data.split("_")[1]
    user_categories[user_id] = category_key
    await callback_query.answer(f"Категория установлена: {CATEGORIES[category_key]}")
    await callback_query.message.edit_text(
        f"✅ Категория установлена: {CATEGORIES[category_key]}\n"
        "Теперь можно начать мониторинг.",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "cancel_category")
async def cb_cancel_category(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Выбор категории отменён.",
        reply_markup=get_main_keyboard()
    )

async def monitor_loop(user_id):
    while monitoring_active.get(user_id, False):
        category = user_categories.get(user_id, "csgo")  # По умолчанию CS:GO
        fp_items = get_funpay_items(category=category)
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
        await asyncio.sleep(random.randint(50, 70))  # Случайная задержка

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
