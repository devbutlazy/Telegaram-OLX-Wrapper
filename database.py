from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")

olx_wrapper = client.olx_wrapper
user_tags = olx_wrapper.user_tags

MAIN_SITE: str = "https://www.olx.ua"
SEARCH_URL: str = (
    # "https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D="
    # "filter_float_price:asc&search%5Bfilter_float_price:from%5D=100"
    "https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D=created_at%3Adesc"
)
NEW_ITEMS_URL: str = (
    "https://www.olx.ua/uk/list/q-{target}/?min_id={last_id}"
    "&reason=observed_search"
    "&search%5Border%5D=created_at%3Adesc"
)

DONATELLO_URL: str = "https://donatello.to/devbutlazy?&c={title}&a=100&m={comment}"


async def get_user_tags(user_id: int) -> Optional[List[str]]:
    if not await user_tags.find_one({"user_id": user_id}):
        return []

    return (await user_tags.find_one({"user_id": user_id})).get("tags", [])


async def get_premium_status(user_id):
    if not await user_tags.find_one({"user_id": user_id}):
        return False

    return (await user_tags.find_one({"user_id": user_id})).get("premium_status", False)


async def create_user(user_id: int, chat_id: int) -> None:
    await user_tags.update_one(
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
