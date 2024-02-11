import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import api.scrapper
from routers import commands, admin, handler

TOKEN = "6548645354:AAFwyuEs25CIBLdPhc3l9vYXqOuaxdyL7v4"
# TOKEN = "5435989927:AAGxoXF6lrD3wvtyUZvv7uJm2acF9HhAdok"


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_routers(commands.router, admin.router, handler.router)
    asyncio.create_task(api.scrapper.main(bot=bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
