#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import re
from datetime import datetime, date


legend = {'temp': 'Temperature [degrees C]',
                'rain': 'Precipitation [nm]',
                'wind_speed': 'Wind speed [km/h]'}
red = 'rgb(22, 96, 167)'
blue = 'rgb(205, 12, 24)'


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
            weather['snow'] = w.get('snow', None)
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
        path_to_today_forecast = './data/*' + today_str + '*' + '.json'
        for f in glob.glob(path_to_today_forecast):
            with open(f, 'rb') as inputfile:
                Json = pickle.loads(inputfile.read())
                self.F.append(Forecast(Json))
        print (len(self.F))
        self.chooseData()


    def chooseData(self):
        """
        Choose data for graph from different sites.
        """
        self.data = {'temp': {}, 'rain': {}, 'wind_speed': {}}
        for f in self.F:
            file_id = f.site + ' ' + str(f.download_date.date())
            x, y_temp, y_rain, y_wind_speed = [], [], [], []
            for d in sorted(f.weather['forecast']):
                x.append(d)
                y_temp.append(f.weather['forecast'][d]['temp'])
                y_rain.append(f.weather['forecast'][d]['rain'])
                y_wind_speed.append(f.weather['forecast'][d]['wind'][0])
            self.data['temp'][file_id] = (x, y_temp)
            self.data['rain'][file_id] = (x, y_rain)
            self.data['wind_speed'][file_id] = (x, y_wind_speed)
        self.generateGraph()


    def generateGraph(self):
        """
        Show graph.
        """
        import plotly
        from plotly.graph_objs import Scatter, Layout, Figure

        fig = plotly.tools.make_subplots(rows=3, cols=1)
        color_site = {'openweath': blue, 'in-pocasi': red}
        for i in range(len(self.quantity)):
            q = self.quantity[i]
            #layout = dict(xaxis=dict(title='Day'), yaxis=dict(title=legend[q]),)
            for site in self.data[q]:
                if site[:14] == 'openweathermap' and q == 'wind_speed':
                    for j in range(len(self.data[q][site][1])):
                        self.data[q][site][1][j] *= 3.6
                if i == 0:
                    fig.append_trace(Scatter(x=self.data[q][site][0],
                        y=self.data[q][site][1],
                        mode='lines+markers', name=site,
                        line=dict(color=color_site[site[:9]])), i+1, 1)
                else:
                    fig.append_trace(Scatter(x=self.data[q][site][0],
                        y=self.data[q][site][1],
                        mode='lines+markers', showlegend=False,
                        line=dict(color=color_site[site[:9]])), i+1, 1)
        fig['layout'].update(title='Forecast comparison')
        fig['layout']['yaxis1'].update(title=legend['temp'])
        filename = './graphs/forecast-comparison-' + self.now_str + '.html'
        plotly.offline.plot(fig, filename=filename)


quantity = ['temp', 'rain', 'wind_speed']
GraphCompareForecast(quantity)
