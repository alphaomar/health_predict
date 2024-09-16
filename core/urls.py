from django.urls import path

from core.views.disease_predictions import DiseasePredictionView
from core.views.home import HomeView
from core.views.doctors import DoctorListView, DoctorDetailView, CreateAppointmentView
from core.views.patients import MedicalRecordShareView, QRCodeView, MedicalHistoryPDFView, PatientProfileView
from patient.views import ConsultationDetailView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('predict/', DiseasePredictionView.as_view(), name='predict_disease'),
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctor/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    path('doctor/<int:pk>/appointment/', CreateAppointmentView.as_view(), name='create_appointment'),
    path('patient/share/<uuid:token>/', MedicalRecordShareView.as_view(), name='view_shared_medical_history'),
    path('patient/<str:email>/qr-code/', QRCodeView.as_view(), name='qr_code_view'),
    path('patient/share/<uuid:token>/pdf/', MedicalHistoryPDFView.as_view(), name='download_medical_history_pdf'),
    path('patient/profile/', PatientProfileView.as_view(), name='patient_profile'),

]
