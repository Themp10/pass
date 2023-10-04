BOT_TOKEN="6536427361:AAFxMGQpo8ZUvDx_WzgXxBhnKKEq2ls4UPk"
WEATHER_API_KEY=" 7a6811847cbe4c1eae2103722230310"

import telebot,requests
from googletrans import Translator

bot = telebot.TeleBot(BOT_TOKEN)
# Dictionary to map weather conditions to emoji icons
weather_icons = {
    "Sunny": "☀️",
    "Partly cloudy": "⛅",
    "Cloudy": "☁️",
    "Overcast": "☁️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Light rain": "🌦️",
    "Moderate rain": "🌧️",
    "Heavy rain": "🌧️",
    "Light snow": "🌨️",
    "Moderate snow": "🌨️",
    "Heavy snow": "🌨️",
    "Thunderstorm": "⛈️",
}

# functions 
def translate_message(message):
    text_to_translate = message.text
    translator = Translator()
    return translator.translate(text_to_translate, dest='en')  # Change 'en' to the target language code if needed


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Mes options : \n 0. /help "
                                                    "\n 1. tradution :/trad "
                                                    "\n 2. Meteo : /weather")

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, " 1. tradution : /trad fr Hello World")

@bot.message_handler(commands=['trad'])
def translate_command(message):
    # Split the message text into command and arguments
    command, *args = message.text.split(maxsplit=2)
    
    if len(args) < 2:
        bot.reply_to(message, "Format de la commande : /trad langue en 2 lettres,fr,en.., mot ou phrase à traduire ex: /trad fr What time is it?.")
    else:
        lang_code, text_to_translate = args[:2]
        translator = Translator()
        translated_text = translator.translate(text_to_translate, dest=lang_code)
        bot.reply_to(message, f"Translation: {translated_text.text}")

@bot.message_handler(commands=['weather'])
def get_weather(message):
    # Split the message text into command and arguments
    command, *args = message.text.split(maxsplit=1)
    
    if len(args) == 0:
        bot.reply_to(message, "Please provide a city name, like '/weather Paris'.")
    else:
        city = args[0]
        weather_data = fetch_weather(city)
        bot.reply_to(message, weather_data)

def fetch_weather(city):
    url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=3'
    #url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}'
    response = requests.get(url)
    data = response.json()
    
    if 'error' in data:
        return f"Sorry, I couldn't fetch the weather data for {city}."
    
    forecast = data['forecast']['forecastday']
    forecast_text = ""
    
    for day in forecast:
        date = day['date']
        condition = day['day']['condition']['text']
        max_temp = day['day']['maxtemp_c']
        min_temp = day['day']['mintemp_c']
         # Get the corresponding emoji icon for the weather condition
        icon = weather_icons.get(condition, "❓")
        
        forecast_text += f"{date} {icon} {condition} {max_temp}°C | {min_temp}°C\n"
    
    return forecast_text
    



@bot.message_handler(func=lambda msg: True)
def reply_to_message(message):

    bot.send_message(message.chat.id, message.text)

bot.infinity_polling()
