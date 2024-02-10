from aiogram import Bot

import asyncio
from datetime import datetime
from typing import Any
import logging
from datetime import datetime, timedelta
import re

import aiohttp
from bs4 import BeautifulSoup
from database import users, NEW_ITEMS_URL, SEARCH_URL, MAIN_SITE

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
    result = await fetch(
        session,
        NEW_ITEMS_URL.format(
            target=tag,
            last_id=data.get("last_id"),
            price_from=data.get("min_amount"),
            price_to=data.get("max_amount"),
        ),
    )
    product_soup = BeautifulSoup(result, "html.parser")
    product_elements = product_soup.find_all("a", class_="css-rc5s2u")

    if product_elements:
        parsed_info = BeautifulSoup(
            await fetch(session, MAIN_SITE + product_elements[0].get("href")),
            "html.parser",
        )
    else:
        logging.error("No product elements found.")

    for element in product_elements:
        parsed_info = BeautifulSoup(
            await fetch(session, f"{MAIN_SITE}{element.get('href')}"), "html.parser"
        )
        if not element.find("p", class_="css-1kyngsx er34gjf0"):
            continue

        if int(
            parsed_info.find("span", class_="css-12hdxwj er34gjf0").text.replace(
                "ID: ", ""
            )
        ) >= data.get("last_id"):
            await users.update_one(
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
            new_date_string = None
            time_match = re.search(
                r"\b(\d{2}:\d{2})\b",
                element.find("p", class_="css-1a4brun er34gjf0").text,
            )
            if time_match:
                time_str = time_match.group(1)
                date_object = datetime.strptime(time_str, "%H:%M")
                new_date_object = date_object + timedelta(hours=2)
                new_time_str = new_date_object.strftime("%H:%M")
                new_date_string = element.find(
                    "p", class_="css-1a4brun er34gjf0"
                ).text.replace(time_str, new_time_str)

            await bot.send_message(
                chat_id=data.get("chat_id"),
                text=(
                    f"<a href='https://i.ibb.co/ZLCdJHt/image.jpg'>📌</a> <b>Нове оголошення по</b> #{tag}\n\n"
                    f"🔗 <b>Посилання:</b> {MAIN_SITE}{element.get('href')}\n"
                    f"📛 <b>Назва:</b> {element.find('h6', class_='css-16v5mdi er34gjf0').text}\n"
                    f"💰 <b>Ціна:</b> {parsed_info.find('h3', class_='css-12vqlj3').text if parsed_info.find('h3', class_='css-12vqlj3') else 'Не вказана'}\n"
                    f"📊 <b>Стан:</b> {element.find('span', class_='css-3lkihg').text if element.find('span', class_='css-3lkihg') else 'Не вказано'}\n"
                    f"📍 <b>Місто:</b> {new_date_string}\n"
                    f"📞 <b>Продавець:</b> {parsed_info.find('h4', class_='css-1lcz6o7 er34gjf0').text} | {parsed_info.find('p', class_='css-b5m1rv er34gjf0').text}\n"
                ),
                parse_mode="html",
            )
            logging.info(f"[{datetime.now().strftime('%H:%M:%S')}] New item found")
        else:
            return logging.info(
                f"[{datetime.now().strftime('%H:%M:%S')}] No new items found"
            )


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

    await users.update_one(
        {"user_id": data.get("user_id")},
        {
            "$set": {
                "last_id": int(
                    parser.find("span", class_="css-12hdxwj er34gjf0").text.replace(
                        "ID: ", ""
                    )
                    if parser.find("span", class_="css-12hdxwj er34gjf0")
                    else data.get("last_id")
                ),
                "tags": data.get("tags"),
            }
        },
        upsert=True,
    )


async def process_tags(bot: Bot, session, data) -> None:
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - bot: Bot - Telegram bot instance
    - session: aiohttp.ClientSession - aiohttp session
    - data: Any - user data for database
    """

    for tags in data.get("tags"):
        for tag, _ in tags.items():
            await check_new_items(bot, session, tag=tag, data=data)


async def get_last_id(tag: str) -> None:
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - tag: str - tag to search for
    """

    async with aiohttp.ClientSession() as session:
        result = await fetch(session, SEARCH_URL.format(target=tag))

    product_soup = BeautifulSoup(result, "html.parser")

    all_list = []
    for element in product_soup.find_all("a", class_="css-rc5s2u"):
        text = element.find("p", class_="css-1a4brun er34gjf0").text
        if text.find("Сьогодні о ") != -1:
            splitted = text.split(" - Сьогодні о ", maxsplit=1)
            async with aiohttp.ClientSession() as session:
                site = await fetch(session, MAIN_SITE + element.get("href"))
            site_soup = BeautifulSoup(site, "html.parser")
            product_id = site_soup.find(
                "span", class_="css-12hdxwj er34gjf0"
            ).text.replace("ID: ", "")
            all_list.append({splitted[1]: product_id})

    last_id_dict = max(all_list, key=lambda x: list(x.keys())[0])
    last_id = list(last_id_dict.values())[0]

    return int(last_id)


async def main(bot: Bot) -> None:
    """
    Start the other services/functions.

    Params:
    - bot: Bot - Telegram bot instance
    """
    logger = logging.getLogger("aiogram")
    logger.info("Successfully scraped all items")
    logger.info("Started loop for checking new items")

    while True:
        async for data in users.find():
            async with aiohttp.ClientSession() as session:
                tags = data.get("tags")

                if tags is None:
                    continue

                if isinstance(tags, int):
                    tags = [tags]

                await process_tags(bot, session, data)
        logger.info("5 Minute Cooldown Started")
        await asyncio.sleep(300)  # 300 seconds = 5 minutes
