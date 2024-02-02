from bs4 import BeautifulSoup
import requests

main_site = "https://www.olx.ua/"
site = requests.get("https://www.olx.ua/uk/list/q-windows-xp/").text

soup = BeautifulSoup(site, "html.parser")

e = soup.find_all("a", class_="css-rc5s2u")

for element in e:
    print("link: ", f"{main_site}{element.get('href')}")
    print("Title:", element.find("h6", class_="css-16v5mdi er34gjf0").text)

    site2 = requests.get(f"{main_site}{element.get('href')}").text

    soup2 = BeautifulSoup(site2, "html.parser")

    e2 = soup2.find_all("div", class_="css-1t507yq er34gjf0")
