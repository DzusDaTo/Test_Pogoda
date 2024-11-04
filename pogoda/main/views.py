from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import WeatherRequest, City
import requests
from django.core.cache import cache
from geopy.geocoders import Nominatim
from .serializers import WeatherRequestSerializer, CitySerializer
import ssl
from rest_framework import generics

ssl._create_default_https_context = ssl._create_unverified_context


class WeatherAPIView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geolocator = Nominatim(user_agent="PogodaApp", timeout=10)

    def get(self, request):
        city_name = request.query_params.get('city')

        if not city_name:
            return Response({'error': 'Пожалуйста, укажите название города'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'weather_{city_name}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        weather_data = self.get_weather_data(city_name)

        if weather_data:
            WeatherRequest.objects.create(city=city_name, request_type='web')

            cache.set(cache_key, weather_data, timeout=30 * 60)  # 30 минут
            return Response(weather_data)
        else:
            return Response({'error': 'Не удалось получить данные о погоде'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_weather_data(self, city_name, access_key='659744ee-d057-4340-bc1f-6c33d1fb76d0'):
        lat, lon = self.get_coordinates(city_name)

        if lat is None or lon is None:
            print(f"Не удалось получить координаты для города: {city_name}")
            return None

        print(f"Координаты для города {city_name}: {lat}, {lon}")

        headers = {
            'X-Yandex-Weather-Key': access_key
        }

        try:
            response = requests.get(f'https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}', headers=headers)
            response.raise_for_status()

            data = response.json()
            print(f"Данные о погоде для {city_name}: {data}")

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


class WeatherRequestListAPIView(APIView):
    def get(self, request):
        queryset = WeatherRequest.objects.all()

        # Фильтрация и пагинация
        request_type = request.query_params.get('type')
        if request_type:
            queryset = queryset.filter(request_type=request_type)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(queryset, request)

        serializer = WeatherRequestSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CityListCreateAPIView(APIView):
    def get(self, request):
        cities = City.objects.all()
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(cities, request)
        serializer = CitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CityDetailAPIView(APIView):
    def get(self, request, id):
        city = City.objects.get(id=id)
        serializer = CitySerializer(city)
        return Response(serializer.data)

    def put(self, request, id):
        city = City.objects.get(id=id)
        serializer = CitySerializer(city, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        city = City.objects.get(id=id)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CityListCreateAPIView(generics.ListCreateAPIView):
    queryset = City.objects.all().order_by('id')
    serializer_class = CitySerializer