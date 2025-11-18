import json
import requests
import os 
import dotenv

dotenv.load_dotenv()

API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')

emoji_dict = {
    "Ясно": "☀️",
    "Небольшая облачность": "🌤️",
    "Облачно с прояснениями": "⛅",
    "Пасмурно": "☁️",
    "Дождь": "🌧️",
    "Сильный дождь": "🌧️",
    "Гроза": "⛈️",
    "Снег": "❄️",
    "Туман": "🌫️",
    "Морось": "💧",
    "Ветрено": "🌬️",
    "Очень жарко": "🥵",
    "Холодно": "🥶",
    "Переменная облачность": "⛅"
}


def get_weather(city, API_WEATHER_TOKEN):
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={API_WEATHER_TOKEN}')
    res = json.loads(response.text)
    
    description = res["weather"][0]["description"].capitalize()
    
    temp = int(res["main"]["temp"])
    
    return (response.status_code, f'{emoji_dict[description]} {description} | {temp}°C')