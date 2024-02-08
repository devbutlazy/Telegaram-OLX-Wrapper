from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from routers.handler import CustomCallback

from database import (
    user_tags,
    get_user_tags,
    create_user,
    get_premium_status,
    DONATELLO_URL,
)
from api.scrapper import get_last_id
from api.donatello import donatello

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Startup command, to add user to database and give information about the bot.

    Params:
    - message: Message - Telegram message
    """

    await create_user(message.from_user.id, message.chat.id)
    await message.answer(
        f"🇺🇦 {hbold(message.from_user.full_name)}, Ласкаво просимо до OLX Wrapper.\n"
        f"Як я можу вам допомогти?",
        reply_markup=(
            InlineKeyboardBuilder()
            .button(text="❓ Деталі", callback_data=CustomCallback(data="information"))
            .as_markup()
        ),
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """
    A command to view the list of available commands.

    Params:
    - message: Message - Telegram message
    """

    await message.answer(
        "🔧 <b>Налаштуйте теги для автоматичного пошуку товарів.</b>\n\n"
        "/add_tag -  Додати новий тег\n"
        "/remove_tag - Видалити тег\n"
        "/view_tags - Подивитись список своїх тегів\n",
        parse_mode="html",
    )


@router.message(Command("add_tag"))
async def add_tag_handler(message: Message) -> None:
    """
    A command to add a new tag to database. (using update_one)
    ~ text.split(maxsplit=1) - split the message into two parts (function call and tag)
    + Free plan == 1 tag
    + Premium plan == 3 tags

    Params:
    - message: Message - Telegram message
    """

    tag: list = message.text.split(maxsplit=1)
    if len(tag) <= 1:
        return await message.answer(
            "❓ Як додати новий тег?\n" '🔵 Приклад: "/add_tag ігровий пк"',
            parse_mode="html",
        )

    tags = await get_user_tags(message.from_user.id)

    if len(tags) >= 1:
        return await message.answer(
            "❗️ <b>Ви не можете додати більше 1-го тегу</b>\n", parse_mode="html"
        )

    if tag[1] in tags:
        return await message.answer(
            "❗️ <b>Такий тег вже є в вашому списку</b>\n", parse_mode="html"
        )

    tags.append(tag[1])

    last_id = await get_last_id(tag[1])

    await user_tags.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"tags": tags, "last_id": last_id}},
        upsert=True,
    )

    await message.answer(
        f'🟢 <b>Тег "#{tag[1]}" успішно додано в базу даних</b>\n'
        "❓ Як тільки з'являться нові оголошення по цій темі, бот автоматично надішле вам сповіщення!\n",
        parse_mode="html",
    )


@router.message(Command("remove_tag"))
async def remove_tag_handler(message: Message) -> None:
    """
    A command to delete a tag from database. (using update_one)
    ~ text.split(maxsplit=1) - split the message into two parts (function call and tag)

    Params:
    - message: Message - Telegram message
    """

    tag: list = message.text.split(maxsplit=1)
    if len(tag) <= 1:
        return await message.answer(
            "❓ Як додати видалити тег?\n" '🔵 Приклад: "/remove_tag ігровий пк"',
            parse_mode="html",
        )

    tags = await get_user_tags(message.from_user.id)

    if len(tags) < 1:
        return await message.answer(
            "❗️ <b>У вас ще немає доданих тегів</b>\n", parse_mode="html"
        )

    if tag[1] not in tags:
        return await message.answer(
            "❗️ <b>Цього тегу немає у списку</b>\n", parse_mode="html"
        )

    tags.remove(tag[1])
    await user_tags.update_one(
        {"user_id": message.from_user.id}, {"$set": {"tags": tags}}, upsert=True
    )

    await message.answer(
        f'🟢 <b>Тег "#{tag[1]}" успішно прибрано з бази даних</b>\n'
        "❓ Бот більше не присилатиме вам сповіщення по цій темі!\n",
        parse_mode="html",
    )


@router.message(Command("view_tags"))
async def view_tags_handler(message: Message) -> None:
    """
    A command to view user tags from database (using get_user_tags function).

    Params:
    - message: Message - Telegram message
    """

    tags = await get_user_tags(message.from_user.id)

    tags_list = "\n".join(f"#{tag}" for tag in tags)

    await message.answer(
        (
            f"❓ <b>Ваші теги:</b>\n{tags_list}"
            if tags
            else "❗️ <b>У вас немає доданих тегів</b>"
        ),
        parse_mode="html",
    )


@router.message(Command("premium"))
async def premium_command_handler(message: Message) -> None:
    """
    A command to view premium status.

    Params:
    - message: Message - Telegram message
    """

    premium_status = await get_premium_status(message.from_user.id)
    if premium_status:
        text = (
            "<b>✔️ Ви придбали OLX Wrapper Pro</b>\n"
            "<b>❗ Тепер у вас збільшений ліміт до трьох тегів!</b>"
        )
    else:
        text = (
            "<b>❌ Ви ще не придбали OLX Wrapper Pro</b>\n"
            "❓ Після придбання преміуму, у вас буде збільшений ліміт тегів (до трьох)!\n"
            "💰 Варість: 100грн"
        )
        reply_markup = InlineKeyboardBuilder().button(
            text="💰 Придбати преміум", url=await donatello.get_donate_url(message.from_user.full_name, message.from_user.id)
        )

    await message.answer(
        text=text,
        parse_mode="html",
        reply_markup=reply_markup.as_markup() if reply_markup else None,
    )
