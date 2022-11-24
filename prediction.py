import requests
import re
from bs4 import BeautifulSoup

BOLD = "\033[;1m"
END = "\033[m"

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
    predicted_matches = {}
    for div in interest_divs:
        teams = div.find('a', class_='').text.replace('\n', '')
        predicted_matches[teams] = {}
        teams_list = teams.split(' - ')
        span = div.find_all(
            'span', class_='px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base')
        for idx, s in enumerate(span):
            predicted_matches[teams][float(s.text)] = teams_list[idx]
    return predicted_matches


def load(predicted_matches):
    for match, prediction in predicted_matches.items():
        print(BOLD + f'{match}' + END + f' -> Expected win for {prediction[min(prediction)]}')
        for odds, team in prediction.items():
            print(f'\t{team} -> {odds}')

if __name__ == '__main__':
    html = extract()
    predicted_matches = transform(html)
    load(predicted_matches)
