import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    PreCheckoutQuery,
    LabeledPrice,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import aiohttp

# Настройки
logging.basicConfig(level=logging.INFO)
bot = Bot(token="7757442937:AAGNqTEdQ_GGjElbU69GKYMn8SfcvVLjTDo")
dp = Dispatcher()

# Конфигурация
API_URL = "https:/invasion-team.ru/telegram/api/ApiPaymet.php"
ADMIN_ID = 123456789
WEBAPP_URL = "https://invasion-team.ru/telegram/casino.html"
PAYMENT_TOKEN = ""

def get_payment_keyboard(amount: int):
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Оплатить {amount} ⭐️", pay=True)
    return builder.as_markup()

@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    web_app_url = f"{WEBAPP_URL}?id={user_id}"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎰 Открыть веб-приложение",
            web_app=WebAppInfo(url=web_app_url))
        ],
        [InlineKeyboardButton(
            text="💳 Пополнить звезды",
            callback_data="choose_topup")
        ]
    ])
    await message.answer(
        "🎉 Испытай удачу! Попробуй выбить дорогой подарок за малую цену!\n\n"
        "➖➖➖➖➖➖➖➖➖➖\n"
        "💎 Для участия тебе понадобятся звезды\n"
        "🔼 Используй кнопку ниже для пополнения",
        reply_markup=keyboard
    )

@dp.callback_query(F.data == "choose_topup")
async def handle_choose_topup(callback: CallbackQuery):
    buttons = [
        [InlineKeyboardButton(text="15 ⭐️", callback_data="topup_15")],
        [InlineKeyboardButton(text="25 ⭐️", callback_data="topup_25")],
        [InlineKeyboardButton(text="50 ⭐️", callback_data="topup_50")],
        [InlineKeyboardButton(text="100 ⭐️", callback_data="topup_100")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.answer("🎯 Выберите количество звезд:", reply_markup=keyboard)
    await callback.answer()

async def create_payment(message: Message, amount: int):
    try:
        prices = [LabeledPrice(label=f"Пополнение {amount} звезд", amount=amount)]
        
        await message.answer_invoice(
            title=f"Пополнение на {amount} ⭐️",
            description=f"Покупка виртуальных звезд для участия в розыгрышах",
            provider_token=PAYMENT_TOKEN,
            currency="XTR",
            prices=prices,
            payload=f"stars_{amount}",
            reply_markup=get_payment_keyboard(amount)
        )
    except Exception as e:
        logging.error(f"Error creating payment: {str(e)}")
        await message.answer("⚠️ Произошла ошибка при создании платежа")

@dp.callback_query(F.data.startswith("topup_"))
async def handle_topup(callback: CallbackQuery):
    try:
        amount = int(callback.data.split("_")[1])
        await create_payment(callback.message, amount)
        await callback.answer()
    except ValueError:
        await callback.answer("⚠️ Неверная сумма пополнения")

@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Произошла ошибка при обработке платежа"
    )

@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    try:
        user_id = message.from_user.id
        amount = int(message.successful_payment.total_amount / 100)
        
        async with aiohttp.ClientSession() as session:
            params = {"id": user_id, "stars": amount}
            
            async with session.get(API_URL, params=params) as response:
                data = await response.json()
                
                if response.status == 200 and data.get('status') == 'success':
                    await message.answer(
                        f"✅ Успешное пополнение!\n"
                        f"▫️ Получено: {amount} ⭐️\n"
                        f"▫️ Теперь у вас: {data['new_stars']} ⭐️\n\n"
                        f"Удачных розыгрышей! 🎲"
                    )
                else:
                    error_msg = data.get('message', 'Unknown error')
                    logging.error(f"API Error: {error_msg}")
                    await message.answer("⚠️ Ошибка обновления баланса. Обратитесь в поддержку @support")
                    
    except Exception as e:
        logging.error(f"Payment processing error: {str(e)}")
        await message.answer("⚠️ Критическая ошибка. Администратор уже уведомлен")
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 Ошибка платежа у @{message.from_user.username}\n"
                 f"ID: {user_id}\n"
                 f"Сумма: {amount} ⭐️\n"
                 f"Ошибка: {str(e)}"
        )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
