from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import DoctorProfile


def chat(request):
    # Display a list of doctors if necessary
    doctors = DoctorProfile.objects.all()
    return render(request, "doctors/doctor_chat.html", {"doctors": doctors})


def room(request, doctor_id):
    # Retrieve the doctor profile using the doctor's ID
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)

    # Use the room_name from the doctor's profile
    room_name = doctor.room_name

    return render(request, "doctors/room.html", {"room_name": room_name, "doctor": doctor})


@login_required
def doctor_room(request):
    # Retrieve the logged-in user's doctor profile
    doctor = get_object_or_404(DoctorProfile, user=request.user)

    # Use the room_name from the doctor's profile
    room_name = doctor.room_name

    return render(request, "doctors/room.html", {"room_name": room_name, "doctor": doctor})
