import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from routers import commands, handler
import scrapper.scrapper

TOKEN = "6548645354:AAFwyuEs25CIBLdPhc3l9vYXqOuaxdyL7v4"
# TOKEN = "5435989927:AAGxoXF6lrD3wvtyUZvv7uJm2acF9HhAdok"  # @запусти


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.include_routers(commands.router, handler.router)
    asyncio.create_task(scrapper.scrapper.main(bot=bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
