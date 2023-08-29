from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("generate_story", views.generate_story, name="generate_story"),
]