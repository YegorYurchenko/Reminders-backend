""" Main-page URL configuration """

from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),
]
