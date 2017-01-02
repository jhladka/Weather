#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import re
from datetime import datetime, date, timedelta


legend = {'temp': 'Temperature [°C]',
                'rain': 'Precipitation [nm]',
                'wind_speed': 'Wind speed [km/h]'}
blue = 'rgb(22, 96, 167)'
red = 'rgb(205, 12, 24)'
green = 'rgb(20, 200, 20)'


class Forecast:

    """
    Reads weather forecast from file.
    """

    def __init__(self, Json):
        self.site = Json['site']
        self.download_date = Json['download_date']
        self.id = Json['id']
        self.weather = {}
        self.weather['forecast'] = {}
        for d, w in Json['forecast'].items():
            weather = {}
            weather['temp'] = w.get('temp', None)
            weather['weather'] = w.get('weather', None)
            weather['clouds'] = w.get('clouds', None)
            weather['wind'] = w.get('wind', [None, None])
            weather['rain'] = w.get('rain', None)
            weather['snow'] = w.get('snow', 0)
            self.weather['forecast'][d] = weather


class GraphCompareForecast:

    """
    Graph.
    """

    def __init__(self, quantity):
        """
        Reads actual forecast's files.
        """
        import pickle
        self.quantity = quantity
        self.now_str = datetime.strftime(datetime.now(),'%Y%m%d%H%M')
        self.F = []
        today_str = self.now_str[0:8]
        path_to_today_forecast = './data/*' + today_str + '*.json'
        for f in glob.glob(path_to_today_forecast):
            with open(f, 'rb') as inputfile:
                Json = pickle.loads(inputfile.read())
                self.F.append(Forecast(Json))
        self.chooseData()


    def chooseData(self):
        """
        Choose data for graph from different sites.
        """
        self.data = {'temp': {}, 'rain': {}, 'wind_speed': {}}
        tmax = '0001-01-01 00:00:00'
        tmin = '9999-01-01 00:00:00'
        for f in self.F:
            file_id = f.site + ' ' + str(f.download_date.date())
            x, y_temp, y_rain, y_wind_speed = [], [], [], []
            forecast = sorted(f.weather['forecast'])
            tmin = min(forecast[0], tmin)
            tmax = max(forecast[-1], tmax)
            for d in forecast:
                x.append(d)
                y_temp.append(f.weather['forecast'][d]['temp'])
                rain = f.weather['forecast'][d]['rain']
                snow = f.weather['forecast'][d]['snow']
                if rain != None and snow != None:
                    y_rain.append(str(float(rain) + float(snow)))
                y_wind_speed.append(f.weather['forecast'][d]['wind'][0])
            self.data['temp'][file_id] = (x, y_temp)
            self.data['rain'][file_id] = (x, y_rain)
            self.data['wind_speed'][file_id] = (x, y_wind_speed)
        dt = timedelta(hours=10)
        self.xmin = datetime.strptime(tmin, '%Y-%m-%d %H:%M:00') - dt
        self.xmax = datetime.strptime(tmax, '%Y-%m-%d %H:%M:00') + dt
        self.generateGraph()


    def generateGraph(self):
        """
        Show graph.
        """
        import plotly
        from plotly.graph_objs import Scatter, Layout, Figure

        fig = plotly.tools.make_subplots(rows=3, cols=1)
        color_site = {'op': blue, 'in': red, 'yr': green}
        for i in range(len(self.quantity)):
            q = self.quantity[i]
            for site in self.data[q]:
                # convert m/s to km/h:
                if q == 'wind_speed':
                    if site[:14] == 'openweathermap' or site[:2] == 'yr':
                        for j in range(len(self.data[q][site][1])):
                            self.data[q][site][1][j] = 3.6 * int(self.data[q][site][1][j])
                if i == 0:
                    fig.append_trace(Scatter(x=self.data[q][site][0],
                        y=self.data[q][site][1],
                        mode='lines+markers', name=site,
                        line=dict(color=color_site[site[:2]])), i+1, 1)
                else:
                    fig.append_trace(Scatter(x=self.data[q][site][0],
                        y=self.data[q][site][1],
                        mode='lines+markers', showlegend=False,
                        line=dict(color=color_site[site[:2]])), i+1, 1)
        fig['layout'].update(title='Forecast comparison')
        fig['layout']['xaxis1'].update(range=[self.xmin, self.xmax])
        fig['layout']['xaxis2'].update(range=[self.xmin, self.xmax])
        fig['layout']['xaxis3'].update(range=[self.xmin, self.xmax])
        fig['layout']['yaxis1'].update(title=legend['temp'])
        fig['layout']['yaxis2'].update(title=legend['rain'])
        fig['layout']['yaxis3'].update(title=legend['wind_speed'])
        filename = './graphs/forecast-comparison-' + self.now_str + '.html'
        plotly.offline.plot(fig, filename=filename)


quantity = ['temp', 'rain', 'wind_speed']
GraphCompareForecast(quantity)
