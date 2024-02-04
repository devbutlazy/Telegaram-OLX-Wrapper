import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

main_site = "https://www.olx.ua"


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main(target: str):
    async with aiohttp.ClientSession() as session:
        url = f"https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D=filter_float_price:asc&search%5Bfilter_float_price:from%5D=100"
        async with session.get(url) as response:
            site = await response.text()

        soup = BeautifulSoup(site, "html.parser")
        elements = soup.find_all("a", class_="css-rc5s2u")

        tasks = [
            fetch(session, f"{main_site}{element.get('href')}") for element in elements
        ]
        pages = await asyncio.gather(*tasks)

        for page in pages:
            parser = BeautifulSoup(page, "html.parser")
            if parser.find("div", class_="css-1jh69qu"):
                print("TOP PREMIUM")

            element = soup.find("a", class_="css-rc5s2u")
            print("Link: ", f"{main_site}{element.get('href')}")
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


if __name__ == "__main__":
    asyncio.run(main(str(input("Enter the good you want to search: "))))
