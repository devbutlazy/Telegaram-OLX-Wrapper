from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardBuilder
from routers.handler import CustomCallback

from database import user_tags, get_user_tags, create_user

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
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


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "🔧 Налаштуйте теги для автоматичного пошуку товарів.\n\n"
        "/add_tag -  🟢 Додати новий тег\n"
        "/remove_tag - 🔴 Видалити тег\n"
        "/view_tags - 🟡 Подивитись список своїх тегів\n",
    )


@router.message(Command("add_tag"))
async def add_tag_handler(message: Message) -> None:
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
    tags = await get_user_tags(message.from_user.id)

    tags_list = "\n".join(f"#{tag}" for tag in tags)

    await message.answer(
        f"🟡 Ваші теги:\n{tags_list}"
        if tags is not None
        else "❗️ У вас немає доданих тегів!"
    )


# print("New item found")

# print("Link: ", f"{MAIN_SITE}{element.get('href')}")
# print("Title:", element.find("h6", class_="css-16v5mdi er34gjf0").text)

# if parsed_info.find("h3", class_="css-12vqlj3"):
#     print("Price:", parsed_info.find("h3", class_="css-12vqlj3").text)

# if element.find("span", class_="css-3lkihg"):
#     print("State:", element.find("span", class_="css-3lkihg").text)

# print(
#     "Location:", element.find("p", class_="css-1a4brun er34gjf0").text
# )
# print(
#     "User: ",
#     parsed_info.find("h4", class_="css-1lcz6o7 er34gjf0").text,
#     " | ",
#     parsed_info.find("p", class_="css-b5m1rv er34gjf0").text,
# )

# print(parsed_info.find("span", class_="css-12hdxwj er34gjf0").text)
# print("-" * 20)