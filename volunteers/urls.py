from django.urls import path
from . import views

app_name = "volunteers"
urlpatterns = [
   path('check_arrival', views.check_arrival, name='arrival'),
   path('check_departure', views.check_departure, name='check_departure'),
]