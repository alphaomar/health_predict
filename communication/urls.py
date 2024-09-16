from django.urls import path
from . import views

app_name = 'communication'  # Namespace for URL reversing

urlpatterns = [
    path("chat/", views.chat, name="chat"),
    path("chat/doctor/<int:doctor_id>/", views.room, name="room"),  # Dynamic URL for the doctor's room
    path("chat/doctor-room/", views.doctor_room, name="doctor_room"),  # Doctor's own chat room
]
