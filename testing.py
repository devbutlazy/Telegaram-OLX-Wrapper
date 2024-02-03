from bs4 import BeautifulSoup
import requests

main_site = "https://www.olx.ua/"
site = requests.get("https://www.olx.ua/uk/list/q-windows-xp/?search%5Border%5D=filter_float_price:asc&search%5Bfilter_float_price:from%5D=100").text

soup = BeautifulSoup(site, "html.parser")

e = soup.find_all("a", class_="css-rc5s2u")

for element in e:
    site2 = requests.get(f"{main_site}{element.get('href')}").text
    soup2 = BeautifulSoup(site2, "html.parser")
    if soup2.find("div", class_="css-1jh69qu"):
        print("TOP PREMIUM")

    print("Link: ", f"{main_site}{element.get('href')}")
    print("Title:", element.find("h6", class_="css-16v5mdi er34gjf0").text)

    if soup2.find("h3", class_="css-12vqlj3"):
        print("Price:", soup2.find("h3", class_="css-12vqlj3").text)

    if element.find("span", class_="css-3lkihg"):
        print("State:", element.find("span", class_="css-3lkihg").text)

    print("Location:", element.find("p", class_="css-1a4brun er34gjf0").text)
    print("User: ", soup2.find("h4", class_="css-1lcz6o7 er34gjf0").text, " | ", soup2.find("p", class_="css-b5m1rv er34gjf0").text)
    print("Views: ", soup2.find("span", class_ = "css-42xwsi", attrs={"data-testid": "page-view-text"}))
    print(soup2.find("div", class_="css-cgp8kk").text.replace("Поскаржитися", ""))
    print("-" * 20)
