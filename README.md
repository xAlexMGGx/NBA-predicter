# IMPORTANT
In order to run this code, the user must have access to the API used, which involves having an api-key. If not, the program will just show the following message: _Could not find api-key_.
In case of having access, the user must introduce the api-key in the _config.txt_ file as shown below:
```
{'auth': '<api-key>'}
```
# NBA-predicter
This is a project based on __webscraping__ and __API data collection__ to elaborate an updated report on the NBA season of an specific team and predict the result of its following games. In this case, we will be using ___Los Angeles Lakers___ as an example. The project is divided in 2 parts.

## 1. PDF report
This part will use both webscraping and API data collection to obtain relevant data for the report. It consists of two _.py_ files:
- extract_news.py
- team_data.py

In order to run both of them, the following libraries must be installed:
- beautifulsoup4
- fpdf
- pandas
- requests

There is a _requirements.txt_ attached in order to install them, with their respective versions.
```
pip install -r requirements.txt
```

#### Extract_news.py
This file is responsible of extracting the latest news related to our NBA team. Using webscraping, it extracts the data from _https://www.rotoballer.com/player-news/page/3?src=single&sport=nba_

It obtains title, date and content of all the relevant news. Then, it generates a _.json_ file with this information.

It is imported during _team_data.py_ in order to introduce these news in our report.

#### Team_data.py
This file is an ETL that obtains the main data from _sportsdata.io_'s __NBA API__, transforms it and loads it into the PDF. It uses three _.json_ files obtained from the API, which provide us of player stats of our team, standings and player information. 

## 2. Prediction of the next games
This part will use webscraping to obtain the odds from the betting house _sportytrader.es_ in order to determine whether our team is expected to win or not the next game. The full url used is the following: _https://www.sportytrader.es/cuotas/baloncesto/usa/nba-306/_

This code is presented in _prediction.py_ file. In order to run it, the following libraries must be installed:
- beautifulsoup4
- requests

Again, both of them are included in _requirements.txt_.
