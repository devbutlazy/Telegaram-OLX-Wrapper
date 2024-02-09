from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from database import (
    IsAdmin,
    add_to_blacklist,
    remove_from_blacklist,
    blacklist
)

router = Router()


@router.message(Command("admin"), IsAdmin())
async def admin_help_handler(message: Message) -> None:
    """
    A command to view the list of available ADMIN commands.

    Params:
    - message: Message - Telegram message
    """

    await message.answer(
        "<a href='https://i.ibb.co/VSJWPkC/image.jpg'>🔒</a> <b>Адмін панель</b>\n\n"
        "/blacklist_add `id` - Додати людину до чорного списку\n"
        "/blacklist_remove `id` - Видалити людину з чорного списку\n"
        "/blacklist_view - Подивитись весь чорний список\n"
        "/view_premium - Подивитись список людей з преміум статусом\n",
        parse_mode="html",
    )


@router.message(Command("blacklist_add"), IsAdmin())
async def blacklist_add_handler(message: Message) -> None:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    """

    identificator: int = message.text.split(maxsplit=1)[1]
    try:
        if message.from_user.id in (await blacklist.find_one({"id": 1})).get(
            "user_list", []
        ):
            return await message.answer(
                text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такий користувач вже є в чорному списку</b>",
                parse_mode="html",
            )

        await add_to_blacklist(user_id=identificator)
        await message.answer(
            text=f"a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви додали {identificator} до чорного списку</b>", parse_mode="html"
        )
    except AttributeError:
        await blacklist.update_one(
            {"id": 1},
            {"$set": {"user_list": [identificator]}},
            upsert=True,
        )
        await message.answer(
            text=f"a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви додали {identificator} до чорного списку</b>", parse_mode="html"
        )


@router.message(Command("blacklist_remove"), IsAdmin())
async def blacklist_remove_handler(message: Message) -> None:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    """
    identificator: int = message.text.split(maxsplit=1)[1]
    try:
        if message.from_user.id not in (await blacklist.find_one({"id": 1})).get(
            "user_list", []
        ):
            await message.answer(
                text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такого користувача немає в чорному списку</b>",
                parse_mode="html",
            )

        await remove_from_blacklist(user_id=identificator)
        await message.answer(
            text=f"<a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви видалили {identificator} з чорного списку</b>", parse_mode="html"
        )
    except AttributeError:
        await blacklist.update_one(
            {"id": 1},
            {"$set": {"user_list": []}},
            upsert=True,
        )
        await message.answer(
            text=f"<a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви видалили {identificator} з чорного списку</b>", parse_mode="html"
        )


@router.message(Command("blacklist_view"), IsAdmin())
async def blacklist_view_handler(message: Message) -> None:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    """
    blacklist_list = (await blacklist.find_one({"id": 1})).get("user_list", [])
    if blacklist_list:
        return await message.answer(
            text=(
                f"<a href='https://i.ibb.co/yNXYfN7/image.jpg'>❗️</a> <b>Чорний список:</b>\n"
                f"User name | {', '.join(str(id) for id in blacklist_list)}"
            ),
            parse_mode="html",
        )

    await message.answer(
        text=f"<a href='https://i.ibb.co/yNXYfN7/image.jpg'>❗️</a> <b>Чорний список пустий!</b>",
        parse_mode="html",
    )
