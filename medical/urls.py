from django.urls import path
from . import views

app_name = "medical"
urlpatterns = [
    path('ambulance', views.ambulance, name='ambulance'),
    path('ambulancelog', views.ambulancelog, name='ambulance_log'),
    path('assigndiseases', views.assign_diseases, name='assign_diseases'),
    
   

]