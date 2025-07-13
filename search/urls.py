from django.urls import path
from .views import semantic_search_view

app_name = "search"

urlpatterns = [
    path("", semantic_search_view, name="semantic_search"),
]
