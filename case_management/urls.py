from django.urls import path
from . import views

app_name = "case_management"
urlpatterns = [
    path("addpost", views.addPost, name="addpost"),
    path("cases", views.retrieveAllPosts, name="cases"),
    path("getcases", views.retrieveSomePosts, name="getcases"),
    path("search", views.serachPost, name="searchPost"),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('CloseCase', views.CloseCase, name='CloseCase'),
    path('addComment', views.addComment, name='addComment')
]