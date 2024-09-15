# chat/urls.py
from django.urls import path

from ai_chat.urls import app_name
from . import views

app_name = 'communication'
urlpatterns = [
    path("", views.chat, name="chat"),
    path("<str:room_name>/", views.room, name="room"),

]
