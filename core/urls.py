from django.urls import path

from core.views.disease_predictions import DiseasePredictionView
from core.views.home import HomeView
from core.views.doctors import DoctorListView, DoctorDetailView, CreateAppointmentView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('predict/', DiseasePredictionView.as_view(), name='predict_disease'),
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctor/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
path('doctor/<int:pk>/appointment/', CreateAppointmentView.as_view(), name='create_appointment'),
    # path('doctor/<int:doctor_id>/create/', AppointmentCreateView.as_view(), name='create_appointment'),

]
