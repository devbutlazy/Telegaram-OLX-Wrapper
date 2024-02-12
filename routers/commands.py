import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold

from api.donatello import Donatello
from api.scrapper import get_last_id
from database import (
    users,
    get_user_tags,
    create_user,
    get_premium_status,
    IsBlacklist,
    regions
)
from routers.handler import CustomCallback

router = Router()
logger = logging.getLogger("aiogram")


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
        "/add_tag -  Додати новий тег (1 - безкоштовно, 3 - преміум)\n"
        "/remove_tag - Видалити тег\n"
        "/view_tags - Подивитись список своїх тегів\n"
        "/premium - Подивитись/придбати інформацію про преміум\n"
        "/price_range - Налаштувати діапазон цін (Преміум)\n\n"
        "/location - Налаштувати фільтр за локацією (Преміум)",
        parse_mode="html",
    )


@router.message(Command("add_tag"), IsBlacklist())
async def add_tag_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to add a new tag to database. (using update_one)
    ~ text.split(maxsplit=1) - split the message into two parts (function call and tag)
    + Free plan == 1 tag
    + Premium plan == 3 tags

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    tag: str = command.args
    if not tag:
        return await message.answer(
            "<a href='https://i.ibb.co/mNS3nt1/image.jpg'>❓</a> <b>Як додати новий тег?</b>\n"
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

    if tag in tags:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такий тег вже є в вашому списку</b>\n",
            parse_mode="html",
        )

    loading = await message.answer(
        "<a href='https://i.ibb.co/VSJWPkC/image.jpg'>❓</a><b>Зачекайте, виконуємо операцію...</b>\n"
    )

    last_id = await get_last_id(tag)
    tags.append({tag: last_id})
    await users.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"tags": tags}},
        upsert=True,
    )

    await loading.edit_text(
        f'<a href="https://i.ibb.co/LC64mF3/image.jpg">🟢</a> <b>Тег "#{tag}" успішно додано в базу даних</b>\n'
        f"❓ Як тільки з'являться нові оголошення по цій темі, бот автоматично надішле вам сповіщення! (Використано {len(tags)} з {limit} тегів)\n",
        parse_mode="html",
    )


@router.message(Command("remove_tag"), IsBlacklist())
async def remove_tag_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to delete a tag from the database. (using update_one)
    ~ text.split(maxsplit=1) - split the message into two parts (function call and tag)

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """
    limit = 3 if await get_premium_status(message.from_user.id) else 1

    tag_arg: str = command.args
    if not tag_arg:
        return await message.answer(
            "<a href='https://i.ibb.co/mNS3nt1/image.jpg'>❓</a> <b>Як видалити тег?</b>\n"
            '🔵 Приклад: "/remove_tag ігровий пк"',
            parse_mode="html",
        )

    user_tags = await get_user_tags(message.from_user.id)

    tag_dict = [
        t_dict for t_dict in user_tags for tag in t_dict.keys() if tag == tag_arg
    ][0]
    tag_name = list(tag_dict.keys())[0]

    if len(user_tags) < 1:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>У вас ще немає доданих тегів</b>\n",
            parse_mode="html",
        )

    if tag_arg not in tag_name:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такого тегу немає в вашому списку</b>\n",
            parse_mode="html",
        )

    user_tags.remove(tag_dict)
    await users.update_one(
        {"user_id": message.from_user.id}, {"$set": {"tags": user_tags}}, upsert=True
    )

    await message.answer(
        f'<a href="https://i.ibb.co/LC64mF3/image.jpg">🟢</a> <b>Тег "#{tag_arg}" успішно прибрано з бази данних.</b>\n'
        f"❓ Тепер бот не буде надсилати сповіщення по цій темі! (Використано {len(user_tags)} з {limit} тегів)\n",
        parse_mode="html",
    )


@router.message(Command("view_tags"), IsBlacklist())
async def view_tags_handler(message: Message) -> None:
    """
    A command to view user tags from database (using get_user_tags function).

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    tags = await get_user_tags(message.from_user.id)

    tags_list = "\n".join(f"#{tag_name}" for tag in tags for tag_name in tag.keys())

    await message.answer(
        (
            f"<a href='https://i.ibb.co/GQgnRsb/image.jpg'>❓</a> <b>Ваші теги ({len(tags)}):</b>\n{tags_list}"
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
    - command: CommandObject - Telegram command
    """

    premium_status = await get_premium_status(message.from_user.id)
    if premium_status:
        text = (
            "<b><a href='https://i.ibb.co/y8C33Yj/image.jpg'>✅</a> Ви придбали OLX Wrapper Pro</b>\n"
            "<b>❗ Тепер у вас збільшений ліміт до трьох тегів та додана можливість налаштовувати діапазон цін!</b>"
        )
        reply_markup = None
    else:
        text = (
            "<a href='https://i.ibb.co/y8C33Yj/image.jpg'>❌</a> <b>Ви ще не придбали OLX Wrapper Pro</b>\n"
            "❓ Після придбання преміуму, у вас буде збільшений ліміт тегів (до трьох) та додана можливість "
            "налаштовувати діапазон ціни!\n"
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


@router.message(Command("price_range"), IsBlacklist())
async def price_range_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    limit = 3 if await get_premium_status(message.from_user.id) else 1
    user_tags = await get_user_tags(message.from_user.id)

    if not await get_premium_status(message.from_user.id):
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>Ця функція доступна лише преміум користувачам (Інформація "
            "- /premium)</b>",
            parse_mode="html",
        )

    if not user_tags:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>У вас ще немає доданих тегів</b>",
            parse_mode="html",
        )

    if not command.args:
        return await message.answer(
            "<a href='https://i.ibb.co/mNS3nt1/image.jpg'>❓</a> <b>Як налаштувати діапазон цін?</b>\n"
            '🔵 Приклад: "/price_range 10 100 (для вимкнення фільтру передайте 0 та 0)"',
            parse_mode="html",
        )

    min_price, max_price = command.args.split()

    try:
        await users.update_one(
            {"user_id": int(message.from_user.id)},
            {
                "$set": {
                    "min_amount": int(min_price),
                    "max_amount": int(max_price),
                }
            },
            upsert=True,
        )
        if min_price == 0 and max_price == 0:
            text = "Фільтр ціни вимкнений."
        else:
            text = f"Тепер теми будуть філтруватись з цінами від {int(min_price)}грн до {int(max_price)}грн"

        await message.answer(
            f'<a href="https://i.ibb.co/LC64mF3/image.jpg">✅</a> <b>{text}</b>\n'
            f"❓ (Використано {len(user_tags)} з {limit} тегів)\n",
            parse_mode="html",
        )

    except BaseException as error:
        logger.error(f"Error: {error}")
        await message.answer(
            text=(
                f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Можливо ви не правильно написали команду!</b>"
                f"\n🔵 Приклад: <b>/price_range 10 100</b>"
            ),
            parse_mode="html",
        )


@router.message(Command("location"), IsBlacklist())
async def location_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    user_tags = await get_user_tags(message.from_user.id)

    if not await get_premium_status(message.from_user.id):
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>Ця функція доступна лише преміум користувачам (Інформація "
            "- /premium)</b>",
            parse_mode="html",
        )

    if not user_tags:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗️</a> <b>У вас ще немає доданих тегів</b>",
            parse_mode="html",
        )

    if not command.args:
        return await message.answer(
            "<a href='https://i.ibb.co/mNS3nt1/image.jpg'>❓</a> <b>Як налаштувати фільтр за локацією?</b>\n"
            '🔵 Приклад: "/location Вінниця" (<b>Вимкнути</b> для вимкнення)',
            parse_mode="html",
        )

    if command.args.capitalize().strip() == "Вимкнути":
        await users.update_one(
            {"user_id": int(message.from_user.id)},
            {
                "$set": {
                    "location": "",
                }
            },
            upsert=True,
        )
        return await message.answer(
            "<a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Фільтр за локацією вимкнено</b>",
            parse_mode="html",
        )

    if not command.args.capitalize().strip() in regions:
        return await message.answer(
            "<a href='https://shorturl.at/svIT4'>❗</a> <b>Не правильний аргумент!</b>\n"
            f"❓ <b>Доступні значення</b>: {', '.join(regions)}\n Або <b>Вимкнути</b> для вимкнення",
            parse_mode="html"
        )

    await users.update_one(
        {"user_id": int(message.from_user.id)},
        {
            "$set": {
                "location": command.args.capitalize().strip(),
            }
        },
        upsert=True,
    )
    await message.answer(
        f"<a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> "
        f"<b>Фільтр за локацією встановлено на {command.args.capitalize().strip()}</b>",
        parse_mode="html",
    )
