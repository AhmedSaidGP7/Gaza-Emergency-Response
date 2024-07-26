from django.urls import path
from . import views

app_name = "medical"
urlpatterns = [
    path('uploadmedicaldocs', views.uploadMedicalFile, name='uploadmedicaldocs'),
    path('ambulance', views.ambulance, name='ambulance'),
    path('ambulancelog', views.ambulancelog, name='ambulance_log'),
    path('assigndiseases', views.assign_diseases, name='assign_diseases'),
    path('ambulancelog/<int:id>/', views.ambulance_log_detail, name='ambulance_log_detail'),
    path('ambulancerecord/<int:id>/', views.ambulance_record_detail, name='ambulance_record_detail'),
    path('diagnose', views.create_diagnose, name='diagnose'), 
    path('addpost', views.addPost, name='addpost'),
    path('allposts', views.retrieveAllPosts, name='allposts'),
    path("getcases", views.retrieveSomePosts, name="getcases"),
    path("search", views.serachPost, name="searchPost"),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('CloseCase', views.CloseCase, name='CloseCase'),
    path('addComment', views.addComment, name='addComment')


    
   

]