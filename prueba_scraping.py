import requests
from bs4 import BeautifulSoup
import re

# URL to scrape
url = 'https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/'

# Get the HTML content
html = requests.get(url).content

# Parse the HTML content
soup = BeautifulSoup(html, 'html.parser')

divs = soup.find_all(
    'div', class_='cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative')

interest_divs = []
for div in divs:
    if re.search('los-angeles-lakers', div.get('onclick')):
        interest_divs.append(div)


for div in interest_divs:
    print(div)
    span = div.find_all(
        'span', class_='px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base')
    teams = div.find('a', class_='')
    print(teams.text.replace('\n', '').split(' - '))
    for s in span:
        print(s.text)
    print('')
