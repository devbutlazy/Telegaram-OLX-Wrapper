from aiogram import Bot

import asyncio
from datetime import datetime
from typing import Any
import logging

import aiohttp
from bs4 import BeautifulSoup
from database import user_tags, NEW_ITEMS_URL, SEARCH_URL, MAIN_SITE

logging.basicConfig(
    format="\033[1;32;48m[%(asctime)s] | %(levelname)s | %(message)s\033[1;37;0m",
    level=logging.INFO,
)


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    """
    Fetch the response content from url.

    Params:
    - session: aiohttp.ClientSession - aiohttp session
    - url: str - url to fetch
    """
    async with session.get(url) as response:
        return await response.text()


# FIXME: Fix the spamming error and make it work correctly
async def check_new_items(
    bot: Bot, session: aiohttp.ClientSession, tag: str, data: Any
) -> None:
    """
    Check for new items and send them to the user.

    Params:
    - bot: Bot - Telegram bot instance
    - session: aiohttp.ClientSession - aiohttp session
    - tag: str - tag name
    - data: Any - data from database
    """

    # ======================================================================================================================================================
    message_text = (
        f"<a href='https://pbt.storage.yandexcloud.net/cp_upload/81dfe15e19c39647389362b9781aa17f_full.png'>📌</a> <b>Нове оголошення по</b> #{tag}\n\n"
        f"🔗 *Посилання:* https://olx.com.ua\n"
        f"📛 *Назва:* Тестування\n"
        f"💰 *Ціна:* 150грн\n"
        f"📊 *Стан:* Б/В\n"
        f"📍 *Місто:* Чернівці, вул. Тиха - 17:09\n"
        f"📞 *Продавець:* Євгеній | Бізнес Аккаунт\n"
    )
    await bot.send_message(
        chat_id=data.get("chat_id"), text=message_text, parse_mode="html"
    )
    # ======================================================================================================================================================

    result = await fetch(
        session, NEW_ITEMS_URL.format(target=tag, last_id=data.get("last_id"))
    )
    product_soup = BeautifulSoup(result, "html.parser")
    product_elements = product_soup.find_all("a", class_="css-rc5s2u")

    if data.get("last_id"):
        parsed_info = BeautifulSoup(
            await fetch(session, MAIN_SITE + product_elements[0].get("href")),
            "html.parser",
        )

        await user_tags.update_one(
            {"user_id": data.get("user_id")},
            {
                "$set": {
                    "last_id": int(
                        parsed_info.find(
                            "span", class_="css-12hdxwj er34gjf0"
                        ).text.replace("ID: ", "")
                    )
                }
            },
        )

        data.update(
            {
                "last_id": int(
                    parsed_info.find(
                        "span", class_="css-12hdxwj er34gjf0"
                    ).text.replace("ID: ", "")
                )
            }
        )

    for element in product_elements:
        logging.info(f"[{datetime.now().strftime('%H:%M:%S')}] New item found")
        parsed_info = BeautifulSoup(
            await fetch(session, f"{MAIN_SITE}{element.get('href')}"), "html.parser"
        )
        if not element.find("p", class_="css-1kyngsx er34gjf0"):
            continue
        if int(
            parsed_info.find("span", class_="css-12hdxwj er34gjf0").text.replace(
                "ID: ", ""
            )
        ) != data.get("last_id"):
            await bot.send_message(
                chat_id=data.get("chat_id"),
                text=(
                    f"<a href='https://pbt.storage.yandexcloud.net/cp_upload/81dfe15e19c39647389362b9781aa17f_full.png'>📌</a> <b>Нове оголошення по</b> #{tag}\n\n"
                    f"🔗 <b>Посилання:</b> {MAIN_SITE}{element.get('href')}\n"
                    f"📛 <b>Назва:</b> {element.find('h6', class_='css-16v5mdi er34gjf0').text}\n"
                    f"💰 <b>Ціна:</b> {parsed_info.find('h3', class_='css-12vqlj3').text if parsed_info.find('h3', class_='css-12vqlj3') else 'Не вказана'}\n"
                    f"📊 <b>Стан:</b> {element.find('span', class_='css-3lkihg').text if element.find('span', class_='css-3lkihg') else 'Не вказано'}\n"
                    f"📍 <b>Місто:</b> {element.find('p', class_='css-1a4brun er34gjf0').text}\n"
                    f"📞 <b>Продавець:</b> {parsed_info.find('h4', class_='css-1lcz6o7 er34gjf0').text} | {parsed_info.find('p', class_='css-b5m1rv er34gjf0').text}\n"
                ),
                parse_mode="html",
            )
        else:
            logging.info(f"[{datetime.now().strftime('%H:%M:%S')}] No new items found")


async def scrape_info(session: aiohttp.ClientSession, element: Any, data: Any) -> None:
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - session: aiohttp.ClientSession - aiohttp session
    - element: Any - elements to search from
    - data: Any - user data
    """
    if element.get("href") == "https://":
        return

    parser = BeautifulSoup(
        await fetch(session, f"{MAIN_SITE}{element.get('href')}"), "html.parser"
    )

    await user_tags.update_one(
        {"user_id": data.get("user_id")},
        {
            "$set": {
                "last_id": int(
                    parser.find("span", class_="css-12hdxwj er34gjf0").text.replace(
                        "ID: ", ""
                    ) if parser.find("span", class_="css-12hdxwj er34gjf0") else data.get("last_id")
                ),
                "tags": data.get("tags"),
            }
        },
        upsert=True,
    )


async def process_tags(bot: Bot, session, data):
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - bot: Bot - Telegram bot instance
    - session: aiohttp.ClientSession - aiohttp session
    - data: Any - user data for database
    """
    for tag in data.get("tags"):
        site = await fetch(session, SEARCH_URL.format(target=tag))
        product_soup = BeautifulSoup(site, "html.parser")
        product_elements = product_soup.find_all("a", class_="css-rc5s2u")

        tasks = [scrape_info(session, element, data) for element in product_elements]
        await asyncio.gather(*tasks)
        await check_new_items(bot, session, tag=tag, data=data)


async def main(bot: Bot):
    """
    Start the other services/functions.

    Params:
    - bot: Bot - Telegram bot instance
    """
    logger = logging.getLogger("aiogram")
    logger.info("Successfully scraped all items")
    logger.info("Started loop for checking new items")

    while True:
        async for data in user_tags.find():
            async with aiohttp.ClientSession() as session:
                tags = data.get("tags")

                if tags is None:
                    continue

                if isinstance(tags, int):
                    tags = [tags]

                await process_tags(bot, session, data)
        logger.info("5 Minute Cooldown Started")
        await asyncio.sleep(300)  # 300 seconds = 5 minutes
