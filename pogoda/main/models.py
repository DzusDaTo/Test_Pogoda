from django.db import models


class WeatherRequest(models.Model):
    city = models.CharField(max_length=255)
    request_time = models.DateTimeField(auto_now_add=True)
    request_type = models.CharField(max_length=50)

    class Meta:
        ordering = ['-request_time']


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name