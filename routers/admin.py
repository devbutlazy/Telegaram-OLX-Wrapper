from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from database import IsAdmin, add_to_blacklist, remove_from_blacklist, blacklist, users

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
        "/add_premium `id` - Додати людині преміум статус\n"
        "/remove_premium `id` - Забрати преміум статус у людини\n"
        "/view_premium - Подивитись список людей з преміум статусом\n",
        parse_mode="html",
    )


@router.message(Command("blacklist_add"), IsAdmin())
async def blacklist_add_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    try:
        if message.from_user.id in (await blacklist.find_one({"id": 1})).get(
            "user_list", []
        ):
            return await message.answer(
                text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такий користувач вже є в чорному списку</b>",
                parse_mode="html",
            )

        await add_to_blacklist(user_id=int(command.args))
        await message.answer(
            text=f"a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви додали {int(command.args)} до чорного списку</b>",
            parse_mode="html",
        )
    except AttributeError:
        await blacklist.update_one(
            {"id": 1},
            {"$set": {"user_list": [int(command.args)]}},
            upsert=True,
        )
        await message.answer(
            text=f"a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви додали {int(command.args)} до чорного списку</b>",
            parse_mode="html",
        )


@router.message(Command("blacklist_remove"), IsAdmin())
async def blacklist_remove_handler(message: Message, command: CommandObject) -> None:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    try:
        if message.from_user.id not in (await blacklist.find_one({"id": 1})).get(
            "user_list", []
        ):
            await message.answer(
                text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такого користувача немає в чорному списку</b>",
                parse_mode="html",
            )

        await remove_from_blacklist(user_id=int(command.args))
        await message.answer(
            text=f"<a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви видалили {int(command.args)} з чорного списку</b>",
            parse_mode="html",
        )
    except AttributeError:
        await blacklist.update_one(
            {"id": 1},
            {"$set": {"user_list": []}},
            upsert=True,
        )
        await message.answer(
            text=f"<a href='https://i.ibb.co/LC64mF3/image.jpg'>✅</a> <b>Ви видалили {int(command.args)} з чорного списку</b>",
            parse_mode="html",
        )


@router.message(Command("blacklist_view"), IsAdmin())
async def blacklist_view_handler(message: Message) -> Message:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    """

    blacklist_list = (await blacklist.find_one({"id": 1})).get("user_list", [])
    if blacklist_list:
        blacklist_user_ids = "\n".join(f"ID: {user_id}" for user_id in blacklist_list)
        return await message.answer(
            text=(
                f"<a href='https://i.ibb.co/yNXYfN7/image.jpg'>❗️</a> <b>Чорний список:</b>\n"
                f"{blacklist_user_ids}"
            ),
            parse_mode="html",
        )

    await message.answer(
        text=f"<a href='https://i.ibb.co/yNXYfN7/image.jpg'>❗️</a> <b>Чорний список пустий!</b>",
        parse_mode="html",
    )


@router.message(Command("add_premium"), IsAdmin())
async def premium_add_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to add a user to the premium users.

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    if not (await users.find_one({"user_id": int(command.args)})):
        return await message.answer(
            text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такого користувача немає в базі даних</b>",
            parse_mode="html",
        )

    try:
        await users.update_one(
            {"user_id": int(command.args)},
            {
                "$set": {
                    "premium_status": True,
                }
            },
            upsert=True,
        )
        await message.answer(
            text=f"<a href='https://i.ibb.co/y8C33Yj/image.jpg'>✅</a> <b>Ви додали преміум статус {int(command.args)}'у</b>",
            parse_mode="html",
        )
    except BaseException:
        await message.answer(
            text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>У цього користувача вже є преміум</b>",
            parse_mode="html",
        )


@router.message(Command("remove_premium"), IsAdmin())
async def premium_remove_handler(message: Message, command: CommandObject) -> Message:
    """
    A command to remove a user from premium users.

    Params:
    - message: Message - Telegram message
    - command: CommandObject - Telegram command
    """

    if not (await users.find_one({"user_id": int(command.args)})):
        return await message.answer(
            text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>Такого користувача немає в базі даних</b>",
            parse_mode="html",
        )

    try:
        await users.update_one(
            {"user_id": int(command.args)},
            {
                "$set": {
                    "premium_status": False,
                }
            },
            upsert=True,
        )
        await message.answer(
            text=f"<a href='https://i.ibb.co/y8C33Yj/image.jpg'>✅</a> <b>Ви забрали преміум статус у {int(command.args)}</b>",
            parse_mode="html",
        )
    except BaseException:
        await message.answer(
            text=f"<a href='https://shorturl.at/svIT4'>❗️</a> <b>У цього користувача не має преміуму</b>",
            parse_mode="html",
        )


@router.message(Command("view_premium"), IsAdmin())
async def premium_view_handler(message: Message) -> Message:
    """
    A command to add a user to the blacklist.

    Params:
    - message: Message - Telegram message
    """

    premium_list = []
    async for data in users.find():
        premium = data.get("premium_status")
        if premium:
            premium_list.append(data.get("user_id"))

    if premium_list:
        premium_user_ids = "\n".join(f"ID: {user_id}" for user_id in premium_list)
        return await message.answer(
            text=(
                f"<a href='https://i.ibb.co/y8C33Yj/image.jpg'>❗️</a> <b>Преміум користувачі:</b>\n"
                f"{premium_user_ids}"
            ),
            parse_mode="html",
        )

    await message.answer(
        text=f"<a href='https://i.ibb.co/y8C33Yj/image.jpg'>❗️</a> <b>Список преміум користувачів пустий!</b>",
        parse_mode="html",
    )
