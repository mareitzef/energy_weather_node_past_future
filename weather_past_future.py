# Import Meteostat library and dependencies
# https://github.com/meteostat/meteostat-python
# https://openweathermap.org/api/one-call-3#how
# pip install plotly
# pip install meteostat
# pip install requests

import pandas as pd
from meteostat import Point, Daily, Hourly, Stations
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotly.offline import plot
import requests
import json
# Dublin Coordinates: 
#lat = "53.34980"
#lon = "-6.260309"

# CCC coordinates
lat = "47.99305"
lon = "7.84068"

# Get nearby weather stations
stations = Stations()
stations = stations.nearby(float(lat),float(lon)) 
station = stations.fetch(1)

# Print closest station 
print(station)

# Time period for the past
start = datetime(2023, 2, 1)
end = datetime(2023, 3, 18)

# The point
point = Point(station['latitude'], station['longitude'], 250)

# Fetch hourly data
data_hourly_Mstat = Hourly(point, start, end)
data_hourly_Mstat = data_hourly_Mstat.fetch()
print(data_hourly_Mstat.head())

# Plot hourly data
# Create a figure with two subplots
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                    specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['dwpt'], name='Hourly Dewpoint Temperature', opacity=0.9, marker=dict(color='orange')), row=1, col=1)
fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['temp'], name='Hourly Temperature'), row=1, col=1)
fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['rhum'], name='Hourly Humidity', line=dict(width=1, dash='dot'),marker=dict(color='grey')), row=1, col=1, secondary_y=True)
fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False, row=1, col=1)
fig.update_yaxes(title_text="Humidity (%)", secondary_y=True, row=1, col=1)

fig.add_trace(go.Bar(x=data_hourly_Mstat.index, y=data_hourly_Mstat['prcp'], name='Hourly Precipitation',  marker=dict(color='blue')), row=2, col=1, secondary_y=True)
fig.add_trace(go.Scatter(x=data_hourly_Mstat.index, y=data_hourly_Mstat['wspd'], name='Wind Speed',opacity=0.7, line=dict(width=1, dash='dot'),marker=dict(color='red')), row=2, col=1)
fig.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
fig.update_yaxes(title_text="Precipitation (mm)", secondary_y=True, row=2, col=1, range=[0, max(data_hourly_Mstat['prcp'])+1])
fig.update_layout(title='Historic Data - Meteostat', height=600)
fig.show()


plot(fig, filename='Meteostat.html', auto_open=True)
api_key = "6545b0638b99383c1a278d3962506f4b"

# Make API request
response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&exclude=current,minutely,daily,alerts&appid={api_key}&units=metric')

# Check if request was successful
if response.status_code == 200:
    # Parse JSON response
    data_OWM = response.json()
    # Print first timestamp
    print(data_OWM['list'][0])
    
    # Extract temperature and wind speed data
    temps = []
    wind_speeds = []
    timestamps = []
    rain_probabs = []
    rains = []
    for i in range(0,len(data_OWM['list'])):
        temp = data_OWM['list'][i]['main']['temp']
        wind_speed = data_OWM['list'][i]['wind']['speed']*3.6
        timestamp = data_OWM['list'][i]['dt_txt']
        rain_probab = data_OWM['list'][i]['pop']*100
        try:
            rain = data_OWM['list'][i]['rain']['3h']
        except KeyError:
            rain = 0


        temps.append(temp)
        wind_speeds.append(wind_speed)
        timestamps.append(timestamp)
        rain_probabs.append(rain_probab)
        rains.append(rain)

    # Create a figure with two subplots
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,specs=[[{}],[{}],[{"secondary_y": True}]])
    # Add traces for temperature and wind speed to the first subplot
    fig.add_trace(go.Scatter(x=timestamps, y=temps, name="Temperature"), row=1, col=1)
    # Add a trace for wind speed to the second subplot
    fig.add_trace(go.Scatter(x=timestamps, y=wind_speeds, name="Wind Speed"), row=2, col=1)
    # Set the y-axis titles for the subplots
    fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)

    fig.add_trace(go.Bar(x=timestamps, y=rains, name='Hourly Precipitation',opacity=0.5,marker=dict(color='blue')), row=3, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=rain_probabs, name='Precipitation Probability',opacity=0.7, line=dict(width=1),marker=dict(color='grey')), row=3, col=1, secondary_y=True)
    fig.update_yaxes(title_text="Precipitation (mm/3h)", row=3, col=1, range=[0, max(rains)+1])
    fig.update_yaxes(title_text="Precipitation Probability (%)", secondary_y=True, row=3, col=1, range=[0, 100])
    fig.update_layout(title='Historic Data - Meteostat', height=600)

    # Update the layout of the figure
    fig.update_layout(title="Openweathermap Forecast", height=600)

    # Show the plot
    fig.show()
    plot(fig, filename='openweathermap.html', auto_open=True)

else:
    print("Error: Request failed")

