from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.transcript_search, name='transcript_search'),
    path("", views.home, name="home"),
]
