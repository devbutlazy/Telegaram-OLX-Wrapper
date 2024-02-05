import asyncio
from datetime import datetime
from typing import Any, Optional
import logging

import aiohttp
from bs4 import BeautifulSoup

MAIN_SITE: str = "https://www.olx.ua"
SEARCH_URL: str = (
    "https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D="
    "filter_float_price:asc&search%5Bfilter_float_price:from%5D=100"
)
NEW_ITEMS_URL: str = (
    "https://www.olx.ua/uk/list/q-{target}/?min_id={last_id}"
    "&reason=observed_search"
    "&search%5Border%5D=filter_float_price:asc"
    "&search%5Bfilter_float_price:from%5D=100"
)

last_id: Optional[int] = None
logging.basicConfig(
    format="\033[1;32;48m[%(asctime)s] | %(levelname)s | %(message)s\033[1;37;0m", 
    level=logging.INFO
)


async def check_new_items(session: aiohttp.ClientSession, tag: str) -> None:
    """
    Check if there are new items on OLX website.
    """
    global last_id

    while True:
        result = await fetch(session, NEW_ITEMS_URL.format(target=tag, last_id=last_id))
        product_soup = BeautifulSoup(result, "html.parser")
        product_elements = product_soup.find_all("a", class_="css-rc5s2u")

        for element in product_elements:
            parsed_info = BeautifulSoup(
                await fetch(session, f"{MAIN_SITE}{element.get('href')}"), "html.parser"
            )

            if parsed_info.find("span", class_="css-12hdxwj er34gjf0").text != last_id:
                print("New item found")

                print("Link: ", f"{MAIN_SITE}{element.get('href')}")
                print("Title:", element.find("h6", class_="css-16v5mdi er34gjf0").text)

                if parsed_info.find("h3", class_="css-12vqlj3"):
                    print("Price:", parsed_info.find("h3", class_="css-12vqlj3").text)

                if element.find("span", class_="css-3lkihg"):
                    print("State:", element.find("span", class_="css-3lkihg").text)

                print(
                    "Location:", element.find("p", class_="css-1a4brun er34gjf0").text
                )
                print(
                    "User: ",
                    parsed_info.find("h4", class_="css-1lcz6o7 er34gjf0").text,
                    " | ",
                    parsed_info.find("p", class_="css-b5m1rv er34gjf0").text,
                )

                print(parsed_info.find("span", class_="css-12hdxwj er34gjf0").text)
                print("-" * 20)

                last_id = parsed_info.find("span", class_="css-12hdxwj er34gjf0").text

        else:
            logging.info(f"[{datetime.now().strftime('%H:%M:%S')}] No new items found")
            await asyncio.sleep(30)


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


async def scrape_info(session: aiohttp.ClientSession, element: Any) -> None:
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - element: Any - elements to search from
    """
    global last_id

    parser = BeautifulSoup(
        await fetch(session, f"{MAIN_SITE}{element.get('href')}"), "html.parser"
    )
    last_id = parser.find("span", class_="css-12hdxwj er34gjf0").text


async def main(tag: str) -> None:
    global last_id

    async with aiohttp.ClientSession() as session:
        site = await fetch(session, SEARCH_URL.format(target=tag))
        product_soup = BeautifulSoup(site, "html.parser")
        product_elements = product_soup.find_all("a", class_="css-rc5s2u")

        tasks = [scrape_info(session, element) for element in product_elements]
        await asyncio.gather(*tasks)
        logging.info(
            f"Successfully scraped items"
        )
        logging.info(
            f"Starting checking for new items...",
        )
        await check_new_items(session, tag=tag)


if __name__ == "__main__":
    asyncio.run(main(str(input("Enter the item you want to search: "))))
