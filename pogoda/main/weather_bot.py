import requests
import ssl
from geopy.geocoders import Nominatim
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = '7729795506:AAE8S_YenNgCIe3_DWiVf3gNJXuWZ84ndso'

ssl._create_default_https_context = ssl._create_unverified_context


class WeatherBot:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="PogodaApp", timeout=10)
        self.access_key = '659744ee-d057-4340-bc1f-6c33d1fb76d0'

    def get_coordinates(self, city_name):
        try:
            location = self.geolocator.geocode(city_name)
            if location is not None:
                return location.latitude, location.longitude
            else:
                print(f"Ошибка: координаты для города '{city_name}' не найдены.")
                return None, None
        except Exception as e:
            print(f"Ошибка получения координат: {e}")
            return None, None

    def get_weather_data(self, city_name):
        lat, lon = self.get_coordinates(city_name)
        if lat is None or lon is None:
            return None

        headers = {
            'X-Yandex-Weather-Key': self.access_key
        }

        try:
            response = requests.get(f'https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}', headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                'temperature': data['fact']['temp'],
                'pressure': data['fact']['pressure_mm'],
                'wind_speed': data['fact']['wind_speed']
            }
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

        return None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Привет! Напишите название города, чтобы узнать погоду.')

    async def get_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        city_name = ' '.join(context.args) if context.args else ''

        if not city_name.strip():
            city_name = update.message.text

        if not city_name.strip():
            await update.message.reply_text('Пожалуйста, укажите название города.')
            return

        weather_data = self.get_weather_data(city_name)
        if weather_data:
            await update.message.reply_text(f"Погода в {city_name}:\n"
                                            f"Температура: {weather_data['temperature']}°C\n"
                                            f"Давление: {weather_data['pressure']} мм\n"
                                            f"Скорость ветра: {weather_data['wind_speed']} м/с")
        else:
            await update.message.reply_text('Не удалось получить данные о погоде.')

    def run(self):
        application = ApplicationBuilder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_weather))

        application.run_polling()


if __name__ == '__main__':
    weather_bot = WeatherBot()
    weather_bot.run()
