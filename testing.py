import time
import aiohttp
import asyncio
import json

from datetime import datetime

import aiofiles

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth

main_site = "https://www.olx.ua"

config = json.load(open("config.json", "r"))
write_to_file = config.get("write_to_file", False)
pages_count = config.get("pages", 1)
timestamp = datetime.now().timestamp()
with_price = config.get("with_price", False)


# async def fetch(session, url):
#     async with session.get(url) as response:
#         return await response.text()


async def main(target: str, driver: webdriver.Chrome, check_title: bool = False):
    """
    Scrape OLX website for listings related to the target item.

    Params:
    - target: str - the item to search for
    - driver: webdriver.Chrome - the Chrome webdriver instance
    - check_title: bool - check if inputed in title
    """
    for page in range(1, pages_count + 1):
        async with aiohttp.ClientSession() as session:
            url = (
                f"https://www.olx.ua/uk/list/q-{target}/"
                + (f"?pages={page}" if page > 1 else "")
                + "&search%5Border%5D=filter_float_price:asc&search%5Bfilter_float_price:from%5D=100"
            )
            async with session.get(url) as response:
                site = await response.text()

            soup = BeautifulSoup(site, "html.parser")
            elements = soup.find_all("a", class_="css-rc5s2u")

            for element in elements:
                driver.get(f"{main_site}{element.get('href')}")

                if check_title:
                    if target.lower() not in driver.title.lower():
                        continue

                driver.maximize_window()

                driver.refresh()

                actions = ActionChains(driver)

                element = driver.find_element(By.CSS_SELECTOR, ".css-ayk4fp")

                actions.move_to_element(element).perform()

                time.sleep(1)

                driver.minimize_window()

                views = driver.find_element(By.CSS_SELECTOR, ".css-42xwsi").text
                link = driver.current_url
                title = driver.title
                location = driver.find_element(By.CSS_SELECTOR, ".css-1cju8pu").text

                if with_price:
                    try:
                        if element := driver.find_element(
                            By.CSS_SELECTOR, ".css-12vqlj3"
                        ):
                            price = element.text
                    except Exception:
                        price = "No price"

                user = driver.find_element(
                    By.CSS_SELECTOR, ".css-rnqkz0 > div:nth-child(2) > h4:nth-child(1)"
                ).text

                try:
                    state = driver.find_element(
                        By.CSS_SELECTOR, "li.css-1r0si1e:nth-child(2) > p:nth-child(1)"
                    ).text
                except Exception:
                    continue

                # title, link, price, location, user, views, state
                print(
                    title,
                    "\n",
                    link,
                    "\n",
                    price,
                    "\n",
                    location,
                    "\n",
                    user,
                    "\n",
                    views,
                    "\n",
                    state,
                    "\n",
                )
                if write_to_file:
                    async with aiofiles.open(
                        f"{target}-{timestamp}.txt",
                        "a",
                        encoding="utf-8",
                    ) as file:
                        await file.write(
                            f"{title}\n{link}\n{price}\n{location}\n{user}\n{views}\n{state}\n\n"
                        )


if __name__ == "__main__":

    category = input("Enter the category you want to search: ")
    config = json.load(open("config.json", "r"))

    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1,1")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)

    stealth(
        driver,
        languages=["en-US", "en", "uk-ua"],
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        vendor="MSI.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    asyncio.run(main(category, driver, config.get("check_title", False)))
