from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from routers.handler import CustomCallback

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"🇺🇸 {hbold(message.from_user.full_name)}, Welcome to OLX Wrapper.\n"
        f"How can I assist you?",
        reply_markup=(
            InlineKeyboardBuilder()
            .button(
                text="❓ Information", callback_data=CustomCallback(data="information")
            )
            .as_markup()
        ),
    )


@router.message(Command("test"))
async def test_handler(message: Message) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="#1",
        callback_data=CustomCallback(data="1"),
    )
    builder.button(
        text="#2",
        callback_data=CustomCallback(data="2"),
    )

    await message.answer("test?", reply_markup=builder.as_markup())
