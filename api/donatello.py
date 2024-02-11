import asyncio
import json
from typing import Union, Any

from aiogram.types import Message
from aiohttp import ClientSession

from database import DONATELLO_URL, users


class Donatello:
    def __init__(self):
        super(Donatello, self).__init__()
        self.__token = "TOKEN"
        self.api = "https://donatello.to/api/v1/donates"
        self.session = ClientSession(headers={"X-Token": self.__token})

    @staticmethod
    async def get_donate_url(user_name: str, user_id: int) -> str:
        return DONATELLO_URL.format(title=user_name, comment=user_id)

    async def get_donates(self) -> Any:
        donates = await self.session.get(self.api)
        text = await donates.read()
        return json.loads(text)["content"] if "content" in json.loads(text) else -1

    async def find_donate(
        self, message: Message, donator: Union[str, int], comment: str
    ) -> Union[Message, str]:
        while True:
            donates = await self.get_donates()
            if donates == -1:
                return "Authentication error"

            for donate in donates:
                if donate["clientName"] == str(donator) and str(
                    donate["message"]
                ) == str(comment):
                    await users.update_one(
                        {"user_id": int(donate["clientName"])},
                        {
                            "$set": {
                                "premium_status": True,
                            }
                        },
                        upsert=True,
                    )
                    return await message.answer(
                        text=(
                            "a href='https://i.ibb.co/y8C33Yj/image.jpg'>✅</a> "
                            "<b>Ви успішно придбали преміум! Дякуємо за підтримку!</b>"
                        ),
                        parse_mode="html",
                    )
            else:
                await asyncio.sleep(5)


donatello = Donatello()
