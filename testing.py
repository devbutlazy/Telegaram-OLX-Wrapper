import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import Any

MAIN_SITE = "https://www.olx.ua"
SEARCH_URL = "https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D=filter_float_price:asc&search%5Bfilter_float_price:from%5D=100"


async def fetch(url: str) -> str:
    """Fetch HTML content from a given URL using aiohttp."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def srape_info(element: Any) -> None:
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - element: Any - elements to search from
    """
    parser = BeautifulSoup(
        await fetch(f"{MAIN_SITE}{element.get('href')}"), "html.parser"
    )

    print("Link: ", f"{MAIN_SITE}{element.get('href')}")
    print("Title:", element.find("h6", class_="css-16v5mdi er34gjf0").text)

    if parser.find("h3", class_="css-12vqlj3"):
        print("Price:", parser.find("h3", class_="css-12vqlj3").text)

    if element.find("span", class_="css-3lkihg"):
        print("State:", element.find("span", class_="css-3lkihg").text)

    print("Location:", element.find("p", class_="css-1a4brun er34gjf0").text)
    print(
        "User: ",
        parser.find("h4", class_="css-1lcz6o7 er34gjf0").text,
        " | ",
        parser.find("p", class_="css-b5m1rv er34gjf0").text,
    )

    print(parser.find("span", class_="css-12hdxwj er34gjf0").text)
    print("-" * 20)


async def main(target: str) -> None:
    """
    Start the other processes.

    Params:
    - target: str - the item to search
    """
    async with aiohttp.ClientSession():
        SITE = await fetch(SEARCH_URL.format(target=target))
        product_soup = BeautifulSoup(SITE, "html.parser")
        product_elements = product_soup.find_all("a", class_="css-rc5s2u")

        tasks = [srape_info(element) for element in product_elements]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main(str(input("Enter the good you want to search: "))))
