from django.shortcuts import render


def chat(request):
    return render(request, "doctors/doctor_chat.html")




def room(request, room_name):
    return render(request, "doctors/room.html", {"room_name": room_name})
