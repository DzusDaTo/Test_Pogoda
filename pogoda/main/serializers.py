from rest_framework import serializers
from .models import WeatherRequest, City


class WeatherRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRequest
        fields = ['id', 'city', 'request_time', 'request_type']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']
