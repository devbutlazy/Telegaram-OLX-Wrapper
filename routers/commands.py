from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from routers.handler import CustomCallback

from database import user_tags, get_user_tags, create_user

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


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """
    A command to view the list of available commands.

    Params:
    - message: Message - Telegram message 
    """
    await message.answer(
        "🔧 Налаштуйте теги для автоматичного пошуку товарів.\n\n"
        "/add_tag -  🟢 Додати новий тег\n"
        "/remove_tag - 🔴 Видалити тег\n"
        "/view_tags - 🟡 Подивитись список своїх тегів\n",
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
            "❓ Як додати новий тег?\n" '🔵 Приклад: "/add_tag ігровий пк"'
        )

    tags = await get_user_tags(message.from_user.id)

    print(tags)
    print(len(tags))
    if len(tags) >= 1:
        return await message.answer("❗️ Ви не можете додати більше 1-го тегу!\n")

    if tag[1] in tags:
        return await message.answer("❗️ Такий тег вже є в вашому списку!\n")

    tags.append(tag[1])

    await user_tags.update_one(
        {"user_id": message.from_user.id}, {"$set": {"tags": tags}}, upsert=True
    )

    await message.answer(
        f'🟢 Тег "#{tag[1]}" успішно додано в базу даних\n'
        "❓ Як тільки з'являться нові оголошення по цій темі, бот автоматично надішле вам сповіщення!\n"
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
            "❓ Як додати видалити тег?\n" '🔵 Приклад: "/remove_tag ігровий пк"'
        )

    tags = await get_user_tags(message.from_user.id)

    if len(tags) < 1:
        return await message.answer("❗️ У вас ще немає доданих тегів!\n")

    if tag[1] not in tags:
        return await message.answer("❗️ Цього тегу немає у списку!\n")

    tags.remove(tag[1])
    await user_tags.update_one(
        {"user_id": message.from_user.id}, {"$set": {"tags": tags}}, upsert=True
    )

    await message.answer(
        f'🟢 Тег "#{tag[1]}" успішно прибрано з бази даних\n'
        "❓ Бот більше не присилатиме вам сповіщення по цій темі!\n"
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
        f"🟡 Ваші теги:\n{tags_list}"
        if tags is not None
        else "❗️ У вас немає доданих тегів!"
    )
