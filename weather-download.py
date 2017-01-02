#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import pickle
from glob import glob
from lxml.html import parse
from datetime import datetime, timedelta


class Forecast:

    """
    Saves the weather.
    """

    def __init__(self, city, date, date_no_spaces):
        self.weather = {}
        self.weather['weather'] = {}
        self.weather['city'] = city
        self.weather['date'] = date
        self.date_no_spaces = date_no_spaces
        self.goto()

    def goto(self):
        """
        Reads weather history.
        """
        if self.weather['city'] == 'Brno':
            # Reads weather from http://pocasi.divoch.cz/:
            self.weather['site'] = 'divoch-Turany'
            html = 'http://pocasi.divoch.cz/historie.php?icao=lktb&fd=' + self.weather['date']
        doc = parse(html).getroot()
        self.parse_response(doc)

    def parse_response(self, doc):
        tr = doc.xpath("//div/div/div[@class='polozky']/table/tr")
        date = []
        temp = []
        Weather = []
        wind = []
        for i in range(len(tr)):
            td = tr[i].xpath("./td")
            regex = re.compile('\d{1,2}:0\d')
            try:
                time = td[0].xpath("./strong")[0].text_content()[:-1] + '0'
            except IndexError:
                continue
            if regex.search(time):
                time = regex.search(time).group()
                date.append(datetime.strptime(self.weather['date'] + time, '%Y-%m-%d%H:%M'))
                temp.append(td[1].xpath("./strong")[0].text_content())
                Weather.append(td[3].text_content())
                regex = re.compile('\d+.*\d*')
                try:
                    wind.append([regex.search(td[5].text_content()[:-4]).group(), None])
                except AttributeError:
                    wind.append([None, None])
        for i in range(len(date)):
            weather = {}
            weather['temp'] = temp[i]
            weather['wind'] = wind[i]
            weather['weather'] = Weather[i]
            self.weather['weather'][str(date[i])] = weather
        #print(self.weather)
        self.saveToFile()

    def saveToFile(self):
        File = './weather/weather-' + self.weather['city'] + '-' + self.date_no_spaces + '.json'
        with open(File, 'wb') as f:
            pickle.dump(self.weather, f)


city = 'Brno'
Today = datetime.today().date()
files = './weather/weather-*.json'
dates = []
for f in glob(files):
    dates.append(datetime.strptime(f[-13:-5], '%Y%m%d').date())
if len(dates) == 0:
    Date = input('Download weather from (YYYY-MM-DD) : ')
    Date = datetime.strptime(Date, '%Y-%m-%d').date()
else:
    Date = sorted(dates)[-1]
    Date += timedelta(days=1)
while Date < Today:
    date = datetime.strftime(Date, '%Y-%m-%d')
    date_no_spaces = datetime.strftime(Date, '%Y%m%d')
    Forecast(city, date, date_no_spaces)
    Date += timedelta(days=1)
