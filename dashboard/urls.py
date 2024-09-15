from django.urls import path

from ai_chat.urls import app_name
from .views import DoctorDashboardView, DoctorProfileDetailView, PatientProfileDetailView, PatientDashboard

app_name = 'dashboard'
urlpatterns = [
    path('doctor-detail/<int:pk>/', DoctorProfileDetailView.as_view(), name='doctor-detail'),
    path('/doctor/', DoctorDashboardView.as_view(), name='doctor_dashboard'),
    path('patient-dashboard/', PatientDashboard.as_view(), name='patient-dashboard'),
    path('patient-detail/<int:pk>/', PatientProfileDetailView.as_view(), name='patient-detail')

]
