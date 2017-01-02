#!/usr/bin/python3
# -*- coding: utf-8 -*-

from grab import Grab
import json
import re
import pickle
from lxml.html import parse
from datetime import datetime, date, time, timedelta

city = 'Brno'
ID = '3078610'    # Brno for OWM
yr_path = {'Brno': 'Czech_Republic/South_Moravia/Brno'}
web_id = {'openweathermap': 'owm', 'in-pocasi': 'inp', 'yr': 'yr'}


class Forecast:

    """
    Saves the weather forecast.
    """

    def __init__(self, site, download_date, ID):
        self.weather = {}
        self.weather['site'] = site
        self.weather['download_date'] = download_date
        self.weather['id'] = ID
        self.weather['forecast'] = {}

    def saveToFile(self):
        site = web_id[self.weather['site']]
        ID = self.weather['id']
        date = datetime.strftime(self.weather['download_date'], '-%Y%m%d%H%M.json')
        inputFile = './data/' + site + '-' + ID + '-' + date
        with open(inputFile, 'wb') as f:
            pickle.dump(self.weather, f)


class ForecastFromYR(Forecast):

    """
    Reads and saves the weather forecast from yr.no into file.
    """

    def __init__(self, city):
        super().__init__('yr', datetime.now(), city)
        self.goto()

    def goto(self):
        """
        Reads weather forecast from yr:
        """
        html = 'http://www.yr.no/place/' + yr_path[city] + '/hour_by_hour_detailed.html'
        doc = parse(html).getroot()
        html_long = 'http://www.yr.no/place/' + yr_path[city] + '/long.html'
        doc_long = parse(html_long).getroot()
        self.parse_response(doc, doc_long)

    def parse_response(self, doc, doc_long):
        temp, rain, wind, clouds, weather, Date = [], [], [], [], [], []
        day = doc.xpath("//table[contains(@class, 'yr-table')]/caption")[0].text_content()
        date_regex = re.compile('[A-S][a-z]{2,8} \d{1,2}, [1-9]\d{3}')
        day = date_regex.search(day).group()
        Time = doc.xpath("//table[contains(@class, 'yr-table')]/tbody/tr/th/strong/text()")
        d = 0
        for t in Time:
            try:
                if t < last_time:
                    d += 1
            except NameError:
                pass
            Date.append(datetime.strptime(day + t, '%B %d, %Y%H:%M') + timedelta(days=d))
            #Date.append(str(datetime.strftime(Datetime, '%Y-%m-%d %H:%M:00')))
            last_time = t
        temp = doc.xpath("//table/tbody/tr/td[contains(@class, 'temperature')]/text()")
        temp = [x[:-1] for x in temp]
        rain = doc.xpath("//table/tbody/tr/td[contains(@title, 'Precipitation:')]/span/text()")
        rain = [x[:-1] for x in rain]
        wind = doc.xpath("//table/tbody/tr/td[contains(@class, 'txt-left')]")
        Wind = [x.text_content() for x in wind]
        wind_regex = re.compile('\d+ m/s')
        wind = []
        for w in Wind:
            exp = wind_regex.search(w)
            if exp != None:
                wind.append([exp.group()[:-4], None])
        clouds = doc.xpath("//table/tbody/tr/td[contains(@title, 'Total cloud-cover:')]/text()")
        clouds = [x[:-2] for x in clouds]
        Weather = doc.xpath("//table[@id='detaljert-tabell']/tbody/tr/td/img[@width='38']/@alt")

        # Long term forecast:
        day_long = doc_long.xpath("//th[@scope='rowgroup']")[0].text_content()[-10:]
        day_long = datetime.strptime(day_long, '%d/%m/%Y')
        temp_long = doc_long.xpath("//table[contains(@id, 'detaljert')]/tr/td[contains(@class, 'temperature')]/text()")
        temp_long = [x[:-1] for x in temp_long]
        rain_long = doc_long.xpath("//table[contains(@id, 'detaljert')]/tr/td[contains(@title, 'Precipitation')]/text()")
        rain_long = [x[:-3] for x in rain_long]
        Wind = doc_long.xpath("//table[contains(@id, 'detaljert')]/tr/td[@class='txt-left']")
        Wind_long = [x.text_content() for x in Wind]
        wind_long = []
        for w in Wind_long:
            exp = wind_regex.search(w)
            if exp != None:
                wind_long.append([exp.group()[:-4], None])
        clouds_long = [None for x in temp_long]
        Weather_long = doc_long.xpath("//table[contains(@id, 'detaljert')]/tr/td/img[@width='38']/@alt")
        weather_long = [x.split('.')[0] for x in Weather_long]
        Time = [x.split()[-1] for x in Weather_long]
        Date_long = []
        for t in Time:
            x = int(t[-11:-9])
            y = int(t[-5:-3])
            if x < y:
                T = int(x + (y - x)/2)
                Date_long.append(datetime.combine(day_long, time(T, 0)))
            else:
                T = int(x + (y - x + 24)/2)
                Date_long.append(datetime.combine(day_long, time(T, 0)))
                day_long += timedelta(days=1)

        # add longterm forecast to list:
        last_date = Date[-1]
        for i in range(len(Date_long)):
            if Date_long[i] <= last_date:
                continue
            Date.append(Date_long[i])
            temp.append(temp_long[i])
            rain.append(rain_long[i])
            wind.append(wind_long[i])
            clouds.append(clouds_long[i])
            Weather.append(weather_long[i])
        #print(len(Date), len(temp), len(rain), len(wind), len(clouds), len(Weather))
        # save it:
        for i in range(len(Date)):
            weather = {}
            weather['temp'] = temp[i]
            weather['rain'] = rain[i]
            weather['wind'] = wind[i]
            weather['clouds'] = clouds[i]
            weather['weather'] = Weather[i]
            self.weather['forecast'][str(Date[i])] = weather
        self.saveToFile()


class ForecastFromInPocasi(Forecast):

    """
    Reads and saves the weather forecast from in-pocasi into file.
    """

    def __init__(self, city):
        super().__init__('in-pocasi', datetime.now(), city)
        self.goto()

    def goto(self):
        """
        Reads weather forecast from in-pocasi:
        """
        html = 'http://www.in-pocasi.cz/predpoved-pocasi/cz/jihomoravsky/brno-25/'
        doc = parse(html).getroot()
        self.parse_response(doc)

    def parse_response(self, doc):
        temp, rain, wind, Date = [], [], [], []
        Today = date.today()
        # 1.day:
        Datetime = datetime.combine(Today, time(1, 0))
        table = doc.find_class('mesto-predpoved')[0]
        div_temp = table.find_class('teplota')
        # Handle class names 'srazky' & 'srazky_ano':
        div_rain = []
        for i in range(8):
            div_id = 'd_sr_h_' + str(100 + i*3)
            div_rain.append(table.get_element_by_id(div_id))
            div_wind = table.find_class('smerovka')
        for div in div_temp:
            temp.append(div.text_content().split()[0])
            Date.append(str(datetime.strftime(Datetime, '%Y-%m-%d %H:%M:00')))
            Datetime += timedelta(hours=3)
        for div in div_rain:
            rain.append(div.text_content().split()[0])
        for div in div_wind:
            wind.append([div.text_content(), None])
        # 2. - 6. day:
        div_dalsi = doc.get_element_by_id('dalsi')
        div_script = div_dalsi.cssselect('script')[0]
        str_temp = re.compile(', t: -?[0-9]*,')
        str_rain = re.compile(', sr: [0-9]*.?[0-9]*,')
        str_wind = re.compile(', vr: [0-9]*,')
        iterator_temp = str_temp.finditer(div_script.text_content())
        iterator_rain = str_rain.finditer(div_script.text_content())
        iterator_wind = str_wind.finditer(div_script.text_content())
        Datetime = datetime.combine(Today + timedelta(days=1), time(1,0))
        for match in iterator_temp:
            temp.append(match.group(0)[5:-1])
            Date.append(str(Datetime))
            Datetime += timedelta(hours=3)
        for match in iterator_rain:
            rain.append(match.group(0)[6:-1])
        for match in iterator_wind:
            wind.append([match.group(0)[6:-1], None])
        # 7. - 12.day:
        div_vyhled = doc.find_class('vyhled')[0]
        vyhled_teploty = div_vyhled.find_class('teplota')
        vyhled_wind = div_vyhled.find_class('smerovka')
        Datetime = datetime.combine(Datetime.date(), time(13, 0))
        for div in vyhled_teploty:
            temp.append(div.text_content().split()[0])
            Date.append(str(Datetime))
            Datetime += timedelta(days=1)
        for div in vyhled_wind:
            rain.append(None)   # no data available
            wind.append([div.text_content(), None])
        for i in range(len(Date)):
            weather = {}
            weather['temp'] = temp[i]
            weather['rain'] = rain[i]
            weather['wind'] = wind[i]
            self.weather['forecast'][str(Date[i])] = weather
        self.saveToFile()


class ForecastFromOWM(Forecast):

    """
    Reads and saves the weather forecast from openweathermap into file.
    """

    def __init__(self, ID):
        super().__init__('openweathermap', datetime.now(), ID)
        self.goto(ID)

    def goto(self, ID):
        """
        Reads weather forecast in json from openweathermap:
        """
        g = Grab()
        s1 = 'http://api.openweathermap.org/data/2.5/forecast?id='
        s2 = '&units=metric&APPID=3e20d3b281497b56c0473aea9c1a888f'
        s = '{s1}{id}{s2}'.format(s1=s1,s2=s2,id=ID)
        g.go(s)
        Json = g.doc.json['list']
        self.parse_response(Json)

    def parse_response(self, Json):
        for w in Json:
            d = w['dt_txt']
            weather = {}
            weather['temp'] = w['main']['temp']
            weather['weather'] = w['weather'][0]['main']
            weather['clouds'] = w['clouds']['all']
            weather['wind'] = [w['wind']['speed'], w['wind']['deg']]
            rain = w.get('rain', {})
            weather['rain'] = rain.get('3h', 0.0)
            snow = w.get('snow', {})
            weather['snow'] = snow.get('3h', 0.0)
            self.weather['forecast'][d] = weather
        self.saveToFile()

ForecastFromYR(city)
ForecastFromOWM(ID)
ForecastFromInPocasi(city)
