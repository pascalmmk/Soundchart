from django.urls import include, path

urlpatterns = [
    path("me/", include("users.urls")),
]
