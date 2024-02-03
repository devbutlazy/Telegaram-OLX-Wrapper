from bs4 import BeautifulSoup
import requests

main_site = "https://www.olx.ua/"


def main(target: str) -> None:
    site = requests.get(
        f"https://www.olx.ua/uk/list/q-{target}/?search%5Border%5D=filter_float_price:asc&search%5Bfilter_float_price:from%5D=100"
    ).text

    soup = BeautifulSoup(site, "html.parser")
    elements = soup.find_all("a", class_="css-rc5s2u")
    for element in elements:
        requested = requests.get(f"{main_site}{element.get('href')}").text
        parser = BeautifulSoup(requested, "html.parser")
        if parser.find("div", class_="css-1jh69qu"):
            print("TOP PREMIUM")

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
    main(str(input("Enter the good you want to search: ")))
