from typing import List, Optional, Dict, Any

from aiogram.filters import BaseFilter
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")

olx_wrapper = client.olx_wrapper
users = olx_wrapper.users
blacklist = olx_wrapper.blacklist

MAIN_SITE: str = "https://www.olx.ua"
SEARCH_URL: str = (
    "https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D=created_at%3Adesc"
)
NEW_ITEMS_URL: str = (
    # "https://www.olx.ua/uk/list/q-{target}/?min_id={last_id}"
    # "&reason=observed_search"
    # "&search%5Border%5D=created_at%3Adesc"
    "https://www.olx.ua/uk/list/q-{target}/?min_id={last_id}"
    "&reason=observed_search&search%5Border%5D=created_at:desc"
    "&search%5Bfilter_float_price:from%5D={price_from}&search%5Bfilter_float_price:to%5D={price_to}"
)
DONATELLO_URL: str = "https://donatello.to/devbutlazy?&c={title}&a=100&m={comment}"

regions = ["Закарпаття", "Львів", "Сумми", "Івано-Франківськ", "Тернопіль", "Харків", "Чернігів", "Черкаси", "Одеса",
           "Київ", "Дніпро", "Херсон", "Полтава", "Рівне", "Чернівці", "Запоріжжя", "Волинь", "Хмельницьк", "Вінниця",
           "Житомир", "Київська обл.", "Миколаїв", "Кіровоград"]


class IsBlacklist(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if await blacklist.find_one({"id": 1}):
            return message.from_user.id not in (
                await blacklist.find_one({"id": 1})
            ).get("user_list", [])
        return True


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in [6456054542, 5986334014]


async def get_user_tags(user_id: int) -> Optional[List[Dict[str, Any]]]:
    if not await users.find_one({"user_id": user_id}):
        return []

    return (await users.find_one({"user_id": user_id})).get("tags", [])


async def get_premium_status(user_id):
    if not await users.find_one({"user_id": user_id}):
        return False

    return (await users.find_one({"user_id": user_id})).get("premium_status", False)


async def add_to_blacklist(user_id: int) -> None:
    blacklist_list = (await blacklist.find_one({"id": 1})).get("user_list", [])
    blacklist_list.append(int(user_id))
    await blacklist.update_one(
        {"id": 1},
        {"$set": {"user_list": blacklist_list}},
        upsert=True,
    )


async def remove_from_blacklist(user_id: int) -> None:
    blacklist_list = (await blacklist.find_one({"id": 1})).get("user_list", [])
    blacklist_list.remove(int(user_id))
    await blacklist.update_one(
        {"id": 1},
        {"$set": {"user_list": blacklist_list}},
        upsert=True,
    )


async def create_user(user_id: int, chat_id: int) -> None:
    if await users.find_one({"user_id": user_id}):
        return
    await users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "chat_id": chat_id,
                "tags": [],
                "last_id": 0,
                "premium_status": False,
                "min_amount": 0,
                "max_amount": 0,
                "location": ""
            }
        },
        upsert=True,
    )
