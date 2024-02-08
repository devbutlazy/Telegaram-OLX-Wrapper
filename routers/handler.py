from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import callback_data
import asyncio
import logging
from api.donatello import donatello
import asyncio

router = Router()


class CustomCallback(callback_data.CallbackData, prefix="data"):
    data: str


@router.callback_query(CustomCallback.filter(F.data))
async def my_callback_foo(query: CallbackQuery, callback_data: CustomCallback):
    """
    Callback query handler for "/" prefixed commands.

    Params:
    - query: CallbackQuery - Telegram callback query
    """

    logging.basicConfig(
        format="\033[1;31;48m[%(asctime)s] | %(levelname)s | %(message)s\033[1;37;0m",
        level=logging.ERROR,
    )

    match callback_data.data:
        case "information":
            message = await query.message.reply(
                f"❓ Я, новий Телеграм-бот - OLX Wrapper.\n"
                f"📕 Моніторю товари, щоб купувати їх за нижчими цінами.\n"
                f"📘 Список команд: /help\n"
            )
            await asyncio.sleep(15)
            await message.delete()
        case "buy_premium":
            asyncio.create_task(
                await donatello.find_donate(
                    query.message, query.from_user.full_name, query.from_user.id
                )
            )
        case _:
            await query.message.reply(
                f"❓ Сталася помилка, повідомте про неї на тех. підтримці!\n"
            )
            logging.error(callback_data.data)
