from django.contrib import admin
from django.urls import path
from .views import *
from music_application import views

urlpatterns = [
    path('', views.UserLogin.as_view(), name='login'),
    path('register', views.UserSignup.as_view(), name='register'),
    path('song/', views.SongView.as_view(), name='song'),
    path('playlists/', views.PlaylistsView.as_view(), name='playlists'),
]