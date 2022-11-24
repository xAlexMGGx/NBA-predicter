import requests
import re
from bs4 import BeautifulSoup


def extract():
    url = 'https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/'
    html = requests.get(url).content
    return html


def transform(html):
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all(
        'div', class_='cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative')
    interest_divs = []
    for div in divs:
        if re.search('los-angeles-lakers', div.get('onclick')):
            interest_divs.append(div)
    return interest_divs