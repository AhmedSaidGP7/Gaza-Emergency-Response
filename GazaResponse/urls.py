from django.urls import path
from . import views

app_name = "GazaReponse"
urlpatterns = [
    path('tesst', views.check_arrival, name='tesst'),
    #path("", views.index, name="index"),
    #path("newyear", views.isNewYear, name="newyear"),
    #path("addtask", views.addTask, name = "addtask"),
   

]