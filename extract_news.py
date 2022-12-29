import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def extract():
    url = 'https://www.rotoballer.com/player-news/page/3?src=single&sport=nba'
    return url


def transform(url):
    current_date = time.time() + 3600
    interest_news_titles = []
    interest_news_content = []
    for i in range(1,11):
        url = f'https://www.rotoballer.com/player-news/page/{i}?src=single&sport=nba'
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'html.parser')
        main_div = soup.find('div', {'class': 'grid_10 alpha newsdesk'})
        titles = main_div.find_all('h4', {'class': 'widget-title teamLogo lakersbg'})
        for t in titles:
            if t.text not in interest_news_titles:
                if len(interest_news_titles) >= 4:
                    break
                interest_news_titles.append(t.text)
        news = main_div.find_all('div', {'class': 'newsdeskContentEntry'})
        for n in news:
            if re.search('agoLos Angeles Lakers', n.text) and n not in interest_news_content:
                interest_news_content.append(n)
            if len(interest_news_content) >= 4:
                break
        if len(interest_news_content) >= 4:
            break
    interest_news = []
    for i, n in enumerate(interest_news_content):
        news_text = n.text
        news_text = re.sub('\nShare:', '', news_text)
        # print(n.prettify())
        date = n.find('span', {'class': 'newsDate'}).text
        if re.search('mins', date):
            date_int = int(date.split(' ')[0])
            news_date = current_date - date_int * 60
            news_date = pd.to_datetime(news_date, unit='s')
        elif re.search('hours', date):
            date_int = int(date.split(' ')[0])
            news_date = current_date - date_int * 3600
            news_date = pd.to_datetime(news_date, unit='s')
        elif re.search('days', date):
            date_int = int(date.split(' ')[0])
            news_date = current_date - date_int * 86400
            news_date = pd.to_datetime(news_date, unit='s')
        else:
            news_date = current_date
            news_date = pd.to_datetime(news_date, unit='s')
        news_text = re.sub(date, '', news_text)
        author_start = re.search('--', news_text).span()[0]
        author = news_text[author_start:]
        author = re.sub(' \n', '', author)
        news_text = re.sub(author, '', news_text)
        author = re.sub(' - ', '\n- ', author)
        interest_news.append({'Title': interest_news_titles[i], 'Content': news_text, 'Date': news_date.strftime(format='%d/%m/%Y'), 'Author': author})
        
    with open('news.json', 'w') as f:
        json.dump(interest_news, f)
        

def main():
    url = extract()
    transform(url)
