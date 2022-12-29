import requests
import re
from bs4 import BeautifulSoup


def extract_data():
    result = {'lal-vs': 0, 'vs-lal': 1}
    url = 'https://www.nba.com/games?date=2022-12-27'
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')
    main_div = soup.find('div', {'class': 'GamesView_gameCardsContainer__c_9fB'})
    divs = main_div.find_all('a', {'class': 'GameCard_gcm__SKtfh GameCardMatchup_gameCardMatchup__H0uPe'})
    for div in divs:
        if re.search('lal', div['href']):
            interesting_div = div
    scores = interesting_div.find_all('p', {'class': 'MatchupCardScore_p__dfNvc GameCardMatchup_matchupScoreCard__owb6w'})
    if re.search('lal-vs', interesting_div['href']):
        lal_score = scores[result['lal-vs']].text
        vs_score = scores[result['vs-lal']].text
    else:
        lal_score = scores[result['vs-lal']].text
        vs_score = scores[result['lal-vs']].text
    print(lal_score, vs_score)

if __name__ == '__main__':
    extract_data()