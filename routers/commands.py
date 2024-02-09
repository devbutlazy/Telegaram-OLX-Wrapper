from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from routers.handler import CustomCallback

from database import (
    users,
    get_user_tags,
    create_user,
    get_premium_status,
    DONATELLO_URL,
    IsBlacklist,
)
from api.scrapper import get_last_id
from api.donatello import Donatello

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
        f"<a href='https://i.ibb.co/HnWmXcG/olxwrappermain.jpg'>🇺🇦</a>{hbold(message.from_user.full_name)}, Ласкаво просимо до OLX Wrapper.\n"
        f"Як я можу вам допомогти?",
        reply_markup=(
            InlineKeyboardBuilder()
            .button(text="❓ Деталі", callback_data=CustomCallback(data="information"))
            .as_markup()
        ),
    )


@router.message(Command("help"), IsBlacklist())
async def help_handler(message: Message) -> None:
    """
    A command to view the list of available commands.

    Params:
    - message: Message - Telegram message
    """

    await message.answer(
        "<a href='https://i.ibb.co/VSJWPkC/image.jpg'>🔧</a><b>Налаштуйте теги для автоматичного пошуку товарів.</b>\n\n"
        "/add_tag -  Додати новий тег\n"
        "/remove_tag - Видалити тег\n"
        "/view_tags - Подивитись список своїх тегів\n",
        parse_mode="html",
    )


@router.message(Command("add_tag"), IsBlacklist())
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
            "<a href='https://i.ibb.co/mNS3nt1/image.jpg'>❓</a> Як додати новий тег?\n"
            '🔵 Приклад: "/add_tag ігровий пк"',
            parse_mode="html",
        )

    tags = await get_user_tags(message.from_user.id)

    limit = 3 if await get_premium_status(message.from_user.id) else 1

    if len(tags) >= limit:
        if limit == 1:
            return await message.answer(
                f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Ви не можете додати більше {limit} тегу(ів)</b>\n"
                f"💰 Придбайте преміум, щоб збільшити ліміт (/premium)",
                parse_mode="html",
            )
        return await message.answer(
            f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Ви не можете додати більше {limit} тегу(ів)</b>\n",
            parse_mode="html",
        )

    if tag[1] in tags:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такий тег вже є в вашому списку</b>\n",
            parse_mode="html",
        )

    loading = await message.answer(
        "<a href='https://i.ibb.co/VSJWPkC/image.jpg'>❓</a><b>Зачекайте, викноуємо операцію...</b>\n"
    )
    
    tags.append(tag[1])
    last_id = await get_last_id(tag[1])
    await users.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"tags": tags, "last_id": last_id}},
        upsert=True,
    )

    await loading.edit_text(
        f'<a href="https://i.ibb.co/LC64mF3/image.jpg">🟢</a> <b>Тег "#{tag[1]}" успішно додано в базу даних</b>\n'
        "❓ Як тільки з'являться нові оголошення по цій темі, бот автоматично надішле вам сповіщення!\n",
        parse_mode="html",
    )


@router.message(Command("remove_tag"), IsBlacklist())
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
            "<a href='https://i.ibb.co/mNS3nt1/image.jpg'>❓</a> Як додати видалити тег?\n"
            '🔵 Приклад: "/remove_tag ігровий пк"',
            parse_mode="html",
        )

    tags = await get_user_tags(message.from_user.id)

    if len(tags) < 1:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>У вас ще немає доданих тегів</b>\n",
            parse_mode="html",
        )

    if tag[1] not in tags:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>Цього тегу немає у списку</b>\n",
            parse_mode="html",
        )

    tags.remove(tag[1])
    await users.update_one(
        {"user_id": message.from_user.id}, {"$set": {"tags": tags}}, upsert=True
    )

    await message.answer(
        f'<a href="https://i.ibb.co/LC64mF3/image.jpg">🟢</a> <b>Тег "#{tag[1]}" успішно прибрано з бази даних</b>\n'
        "❓ Бот більше не присилатиме вам сповіщення по цій темі!\n",
        parse_mode="html",
    )


@router.message(Command("view_tags"), IsBlacklist())
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
            f"<a href='https://i.ibb.co/GQgnRsb/image.jpg'>❓</a> <b>Ваші теги:</b>\n{tags_list}"
            if tags
            else "<a href='https://i.ibb.co/GQgnRsb/image.jpg'>❗️</a> <b>У вас немає доданих тегів</b>"
        ),
        parse_mode="html",
    )


@router.message(Command("premium"), IsBlacklist())
async def premium_command_handler(message: Message) -> None:
    """
    A command to view premium status.

    Params:
    - message: Message - Telegram message
    """

    premium_status = await get_premium_status(message.from_user.id)
    if premium_status:
        text = (
            "<b><a href='https://i.ibb.co/y8C33Yj/image.jpg'>✅</a> Ви придбали OLX Wrapper Pro</b>\n"
            "<b>❗ Тепер у вас збільшений ліміт до трьох тегів!</b>"
        )
        reply_markup = None
    else:
        text = (
            "<a href='https://i.ibb.co/y8C33Yj/image.jpg'>❌</a> <b>Ви ще не придбали OLX Wrapper Pro</b>\n"
            "❓ Після придбання преміуму, у вас буде збільшений ліміт тегів (до трьох)!\n"
            "💰 Варість: 100грн"
        )
        reply_markup = InlineKeyboardBuilder().button(
            text="💰 Придбати преміум",
            url=await Donatello.get_donate_url(
                message.from_user.full_name, message.from_user.id
            ),
        )
    await message.answer(
        text=text,
        parse_mode="html",
        reply_markup=reply_markup.as_markup() if reply_markup else None,
    )
