from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_transcript_tsv, name='upload_transcript'),
    path('upload_canvas/', views.upload_canvas_json, name='upload_canvas_json'),
    path('upload/success/', views.upload_success, name='upload_success'),

]
