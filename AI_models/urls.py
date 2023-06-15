from django.urls import path, include
from . import views

app_name = 'AI_models'

urlpatterns = [
    path('personality_detect/', views.personality_detect, name="personality_detect")
]