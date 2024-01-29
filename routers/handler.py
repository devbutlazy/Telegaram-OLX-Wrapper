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
                f"❓ I am an advanced Telegram Bot - OLX Wrapper.\n"
                f"📕 I monitor goods to buy them at lower prices.\n"
                f"📘 Commands list: /start , /test \n"
            )
            await asyncio.sleep(15)
            await message.delete()
