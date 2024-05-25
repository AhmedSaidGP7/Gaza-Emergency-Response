from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path("", views.index, name="index"),
    path("auth", views.auth, name="login"),
    path("signout", views.signout, name="signout")
]