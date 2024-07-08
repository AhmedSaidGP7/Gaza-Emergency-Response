from django.urls import path
from . import views


app_name = "operations"
urlpatterns = [
    path("addperson", views.addPerson, name="addperson"),
    path("addcasualty" , views.addCasualty, name="addcasualty"),
    path("accommodation" , views.accommodation, name="accommodation"),
    path("customers", views.customers, name="customers"),
    path("shelters", views.sheltersStat, name="shelters"),
    path("shelter/<int:shelter_id>/", views.shelterDetails, name="shelterDetails"),
    path("freespots/<int:shelter_id>/", views.availableApartments, name="freespots"),
    path('profile/<int:person_id>/', views.profile, name='profile'),
    path("remove", views.removePerson, name='remove'),
    path("reomved", views.customersOut, name="removed"),
    path('upload_excel/', views.upload_excel, name='upload_excel'),
   

    
]