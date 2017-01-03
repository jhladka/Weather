#!/usr/bin/python3
# -*- coding: utf-8 -*-


"""

Compare forecast accuracy as a function of number of days prior to the forecast date.

Y-axis shows the difference between weather and forecast values.
So, values above zero axis mean that the weather values were higher than
predicted and conversely values below 0 indicate the forecast overestimated
the weather.

"""


import glob
import re
import pickle
from datetime import datetime, timedelta


legend = {'temp': "Δ Temperature [°C]",
          'wind_speed': 'Δ Wind speed [km/h]'}
blue = 'rgb(22, 96, 167)'
red = 'rgb(205, 12, 24)'
green = 'rgb(20, 200, 20)'


class Weather:

    """
    Reads weather from files.
    """

    def __init__(self, city):
        self.data = {}
        path_to_weather = './weather/weather-' + city + '-*.json'
        for f in glob.glob(path_to_weather):
            with open(f, 'rb') as inputfile:
                Json = pickle.loads(inputfile.read())
                for d, w in Json['weather'].items():
                    self.data[d] = w


class GraphWeatherVsForecast:

    """
    Graph.
    """

    def __init__(self, quantity):
        """
        Reads forecast and weather files.
        """
        self.weather = Weather(city)
        self.delta = {}
        for s in site:
            self.delta[s] = {}
            for q in quantity:
                self.delta[s][q] = {}
            path_to_forecast = './data/' + site[s][0] + '-' + site[s][1] + '--*.json'
            for f in glob.glob(path_to_forecast):
                with open(f, 'rb') as inputfile:
                    Json = pickle.loads(inputfile.read())
                    self.addData(s, Json)
        self.showGraph()


    def addData(self, site, forecast):
        forecast_download_date = forecast['download_date']
        for weather in self.weather.data:
            if weather in forecast['forecast']:
                weather_date = datetime.strptime(weather, '%Y-%m-%d %H:%M:%S')
                deltatime = roundTimeDelta(weather_date - forecast_download_date)
                if deltatime < timedelta(0) or deltatime > timedelta(6):
                    continue
                for q in quantity:
                    if q == 'wind_speed':
                        weather_wind = self.weather.data[weather]['wind'][0]
                        forecast_wind = forecast['forecast'][weather]['wind'][0]
                        if weather_wind != None and forecast_wind != None:
                            qdelta = float(weather_wind) - float(forecast_wind)
                            if site in wind_speed_convert:
                                qdelta *= 3.6
                    else:
                        weather_q = self.weather.data[weather][q]
                        forecast_q = forecast['forecast'][weather][q]
                        if weather_q != None and forecast_q != None:
                            qdelta = float(weather_q) - float(forecast_q)
                    try:
                        self.delta[site][q][deltatime].append(qdelta)
                    except KeyError:
                        self.delta[site][q][deltatime] = [qdelta]


    def showGraph(self):
        """
        Show graph.
        """
        from math import sqrt
        import plotly
        from plotly.graph_objs import Scatter, Box, Layout, Figure
        import requests

        fig = plotly.tools.make_subplots(rows=2, cols=1)
        color_site = {'op': blue, 'in': red, 'yr': green}
        for site in self.delta:
            for q in quantity:
                x_scatter, y_scatter = [], []
                x, y_mean, y_stdDev = [], [], []
                for i in self.delta[site][q]:
                    N = len(self.delta[site][q][i])
                    if N > 1:
                        x.append(i.days + i.seconds/86400)
                        y_mean.append(sum(self.delta[site][q][i])/N)
                        stdDev = 0
                        for j in self.delta[site][q][i]:
                            x_scatter.append(i.days + i.seconds/86400)
                            y_scatter.append(j)
                            stdDev += (j - y_mean[-1])**2
                        y_stdDev.append(sqrt(stdDev/(N - 1)))
                color = color_site[site[:2]]
                if q == 'temp':
                    qq = 'temperature'
                    subplot = 1
                else:
                    qq = q
                    subplot = 2
                fig.append_trace(
                    Box(x=x_scatter, y=y_scatter, name=site + ': ' + qq,
                        line=dict(color=color_site[site[:2]])), subplot, 1)
        fig['layout'].update(title='Weather vs. Forecast comparison - ' + city)
        fig['layout']['xaxis1'].update(title='days ahead')
        fig['layout']['xaxis2'].update(title='days ahead')
        fig['layout']['yaxis1'].update(title=legend['temp'])
        fig['layout']['yaxis2'].update(title=legend['wind_speed'])
        now_str = datetime.strftime(datetime.now(),'%Y%m%d%H%M')
        try:
            filename = 'Weather_vs_forecast'
            plotly.plotly.plot(fig, filename=filename)
        except requests.exceptions.ConnectionError:
            filename = './graphs/weather-vs-forecast-' + city + '-' + now_str + '.html'
            plotly.offline.plot(fig, filename=filename)



def roundTimeDelta(delta):
    """
    Rounds timedelta to 'h' hours
    """
    h = 3
    r = h * 3600
    s = delta.seconds
    d = s - s%r + ((s%r + r/2)//r)*r
    return timedelta(days=delta.days, seconds=d)


city = 'Brno'
site = {'in-pocasi': ['inp', 'Brno'],
        'yr': ['yr', 'Brno'],
        'openweathermap': ['owm', '3078610']}
quantity = ['temp', 'wind_speed']
wind_speed_convert = {'yr', 'openweathermap'}   # output is in km/h
GraphWeatherVsForecast(quantity)
