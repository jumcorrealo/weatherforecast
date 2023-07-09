import os
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,PHONE_NUMBER,API_KEY_WAPI,K_NUMBER,J_NUMBER
import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime
from utils import request_wapi,get_forecast,create_df,send_message,get_date


query = 'Bogotá'
api_key = API_KEY_WAPI

url = 'http://api.weatherapi.com/v1/forecast.json?key={}&q={}&days=1&aqi=no&alerts=no'.format(api_key,query)

input_date= get_date()
response = requests.get(url).json()

def get_forecast(response,i):

    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0]
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temp = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    rain_prov = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']
    
    return fecha,hora,condicion,temp,rain,rain_prov

datos = []

for i in tqdm(range(len(response['forecast']['forecastday'][0]['hour'])), colour = 'green'):

    datos.append(get_forecast(response,i))


col = ['Fecha','Hora','Condicion','Temp','Rain','Rain_prov']
df = pd.DataFrame(datos,columns=col)
df_rain = df[(df['Rain'] == 1)]
df_redu = df_rain[['Hora','Temp','Condicion']]
df_redu.set_index('Hora',inplace = True)
df_temp = df[['Hora','Temp','Condicion']]


current_hour = str(datetime.now().time().hour)
if len(current_hour) == 1:
    current_hour = current_hour.zfill(2)

df_temp = df_temp[df_temp['Hora'] == current_hour]
df_temp.set_index('Hora',inplace = True)

k = K_NUMBER
j = J_NUMBER
time.sleep(2)
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN


client = Client(account_sid, auth_token)
if df_redu.empty:
    template = '\n Hoy no hay arrunchis, no va a llover :c \n\n\n ' + str(df_redu) 
else:
    template = '\n Hoy va a llover en '+ query +', abrígate bien :) \n\n\n ' + str(df_temp)

message = client.messages \
    .create(
        
        body=template,
        from_=PHONE_NUMBER,
        to=k
     )

print('Mensaje enviado: ',message.sid, template)
