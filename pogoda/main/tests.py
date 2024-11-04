import pytest
from unittest.mock import patch, MagicMock

from .weather_bot import WeatherBot


from rest_framework import status
from rest_framework.test import APIClient
from .models import WeatherRequest, City


class TestWeatherBot:
    @pytest.fixture
    def weather_bot(self):
        return WeatherBot()

    @patch('weather_bot.Nominatim')
    def test_get_coordinates_success(self, mock_geolocator, weather_bot):
        mock_location = MagicMock()
        mock_location.latitude = 55.7558
        mock_location.longitude = 37.6173
        mock_geolocator.return_value.geocode.return_value = mock_location

        lat, lon = weather_bot.get_coordinates("Москва")

        assert lat == 55.625578
        assert lon == 37.6063916

    @patch('weather_bot.requests.get')
    def test_get_weather_data_success(self, mock_requests, weather_bot):
        # Настройка имитации
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'fact': {
                'temp': 10,
                'pressure_mm': 750,
                'wind_speed': 5
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.return_value = mock_response

        weather_data = weather_bot.get_weather_data("Москва")

        assert weather_data['temperature'] == 10
        assert weather_data['pressure'] == 750
        assert weather_data['wind_speed'] == 5

    @patch('weather_bot.requests.get')
    def test_get_weather_data_http_error(self, mock_requests, weather_bot):
        mock_requests.side_effect = Exception("Ошибка")

        weather_data = weather_bot.get_weather_data("Москва")

        assert weather_data is None


@pytest.mark.django_db
class TestWeatherAPIView:
    client = APIClient()

    def test_get_weather_without_city(self):
        response = self.client.get('/weather/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {'error': 'Пожалуйста, укажите название города'}

    @patch('main.views.WeatherAPIView.get_coordinates')
    @patch('main.views.WeatherAPIView.get_weather_data')
    def test_get_weather_with_valid_city(self, mock_get_weather_data, mock_get_coordinates):
        mock_get_coordinates.return_value = (55.7558, 37.6173)
        mock_get_weather_data.return_value = {
            'temperature': 5,
            'pressure': 740,
            'wind_speed': 3
        }

        response = self.client.get('/weather/?city=Москва')
        assert response.status_code == status.HTTP_200_OK
        assert 'temperature' in response.data

    @patch('main.views.WeatherAPIView.get_coordinates')
    def test_get_weather_with_invalid_city(self, mock_get_coordinates):
        mock_get_coordinates.return_value = (None, None)

        response = self.client.get('/weather/?city=НеизвестныйГород')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data == {'error': 'Не удалось получить данные о погоде'}


@pytest.mark.django_db
class TestWeatherRequestListAPIView:
    client = APIClient()

    def test_get_weather_requests(self):
        WeatherRequest.objects.create(city='Москва', request_type='web')

        response = self.client.get('/requests/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0


@pytest.mark.django_db
class TestCityListCreateAPIView:
    client = APIClient()

    def test_get_cities(self):
        response = self.client.get('/cities/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_city(self):
        data = {'name': 'Москва'}
        response = self.client.post('/cities/', data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert City.objects.filter(name='Москва').exists()

    def test_create_city_invalid(self):
        data = {'name': ''}
        response = self.client.post('/cities/', data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCityDetailAPIView:
    client = APIClient()

    def setup_method(self):
        self.city = City.objects.create(name='Москва')

    def test_get_city(self):
        response = self.client.get(f'/cities/{self.city.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Москва'

    def test_update_city(self):
        data = {'name': 'Санкт-Петербург'}
        response = self.client.put(f'/cities/{self.city.id}/', data=data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Санкт-Петербург'

    def test_delete_city(self):
        response = self.client.delete(f'/cities/{self.city.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not City.objects.filter(id=self.city.id).exists()
