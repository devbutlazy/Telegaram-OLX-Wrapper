from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram.filters import BaseFilter
from aiogram.types import Message

client = AsyncIOMotorClient("mongodb://localhost:27017")

olx_wrapper = client.olx_wrapper
users = olx_wrapper.users
blacklist = olx_wrapper.blacklist

MAIN_SITE: str = "https://www.olx.ua"
SEARCH_URL: str = (
    "https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D=created_at%3Adesc"
)
NEW_ITEMS_URL: str = (
    "https://www.olx.ua/uk/list/q-{target}/?min_id={last_id}"
    "&reason=observed_search"
    "&search%5Border%5D=created_at%3Adesc"
)
DONATELLO_URL: str = "https://donatello.to/devbutlazy?&c={title}&a=100&m={comment}"


class IsBlacklist(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id not in (await blacklist.find_one({"id": 1})).get(
            "user_list", []
        )


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in [6456054542, 5986334014]


class IsPremium(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return (await users.find_one({"user_id": message.from_user.id})).get(
            "premium_status", False
        )


async def get_user_tags(user_id: int) -> Optional[List[str]]:
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
                "last_id": 0,
                "tags": [],
                "premium_status": False,
            }
        },
        upsert=True,
    )
