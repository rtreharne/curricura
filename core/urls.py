from django.urls import path
from . import views

urlpatterns = [
    path('demo/', views.demo, name='demo'),
    path("demo/search/", views.semantic_search_demo, name="semantic_search_demo"),
    path("demo/chat/", views.ai_chat_demo, name="ai_chat_demo"),
    path("", views.home, name="home"),
]
