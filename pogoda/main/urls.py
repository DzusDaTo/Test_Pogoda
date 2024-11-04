from django.urls import path
from .views import WeatherAPIView, WeatherRequestListAPIView, CityListCreateAPIView, CityDetailAPIView

urlpatterns = [
    path('weather/', WeatherAPIView.as_view(), name='weather_api'),
    path('requests/', WeatherRequestListAPIView.as_view(), name='weather_requests'),
    path('cities/', CityListCreateAPIView.as_view(), name='city_list'),
    path('cities/<int:id>/', CityDetailAPIView.as_view(), name='city_detail'),
]
