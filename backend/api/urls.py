from django.urls import path, include
urlpatterns = [
  path("auth/", include("authn.urls")),
  path("public/", include("music.public_urls")),
  path("me/", include("users.urls")),
]
