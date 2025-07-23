# chat/urls.py

from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.chat_home, name="chat_home"),
    path('course/<int:course_id>/', views.chat_course, name='chat_course'),
    path("ai_chat/", views.ai_chat, name="ai_chat"),
]
