from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import callback_data
import asyncio

router = Router()


class CustomCallback(callback_data.CallbackData, prefix="data"):
    data: str


@router.callback_query(CustomCallback.filter(F.data))
async def my_callback_foo(query: CallbackQuery, callback_data: CustomCallback):
    match callback_data.data:
        case "1":
            await query.answer("1")
        case "2":
            await query.answer("2")
        case "information":
            message = await query.message.reply(
                f"❓ Я просунутий Telegram-бот - OLX Wrapper.\n"
                f"📕 Моніторю товари, щоб купувати їх за нижчими цінами.\n"
                f"📘 Список команд: /help\n"
            )
            await asyncio.sleep(15)
            await message.delete()
