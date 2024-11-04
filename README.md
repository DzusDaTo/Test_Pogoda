# Test_pogoda
## Описание
### Test_pogoda — это тестовое веб-приложение для получения текущей погоды по заданному городу. Пользователи могут запрашивать информацию о погоде и сохранять историю своих запросов. Приложение использует внешние API для геокодирования и получения данных о погоде.

#### Стек технологий:

- Django — веб-фреймворк для создания серверной части приложения.
- Django REST Framework — для построения RESTful API.
- SQLite — легковесная реляционная база данных для хранения информации о городах и запросах погоды.
- pytest — для написания и запуска тестов.
- Requests — для выполнения HTTP-запросов к внешним API.
  
#### Установка

##### Клонирование репозитория

```
git clone https://github.com/DzusDaTo/Test_Pogoda.git
cd Test_Pogoda
```

Установка зависимостей

```
pip install -r requirements.txt
```

Миграции

```
python manage.py migrate
```

Запуск приложения

```
python manage.py runserver
```

## API

### Эндпоинты

#### Получение погоды
1. URL: /api/weather/
2. Метод: GET
3. Ответ:
```
{
    "temperature": 0,
    "pressure": 742,
    "wind_speed": 4.4
}
```

#### Запросы погоды
1. URL: /api/weather-requests/
2. Метод: GET

#### Список городов
1. URL: /api/cities/
2. Метод: GET

#### Создание города
1. URL: /api/cities/
2. Метод: POST
3. Тело запроса:
  - JSON-объект с полем name — название города.
4. Ответ:
 - JSON-объект с данными созданного города.

#### Детали города
1. URL: /api/cities/<int:id>/
2. Метод: GET, PUT, DELETE
3. Ответ:
  - JSON-объект с данными города (для GET),
обновленные данные города (для PUT),
статус удаления (для DELETE).
