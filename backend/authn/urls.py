from django.urls import path
from . import views
urlpatterns = [
  path("spotify/login", views.spotify_login),
  path("spotify/callback", views.spotify_callback),
  path("logout", views.auth_logout),
  path("me", views.me),
]
