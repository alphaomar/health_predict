from django.urls import path

from accounts.urls import app_name
from .views import chat_view

app_name = "ai_chat"
urlpatterns = [
   path('chat/', chat_view, name='chat'),
]