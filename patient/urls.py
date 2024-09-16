from django.urls import path

from core.urls import app_name
from .views import generate_qr_code_view
from .views import PatientMedicalRecordListView, ConsultationDetailView

app_name='patient'
urlpatterns = [
    path('patient/qr/<uuid:token>/', generate_qr_code_view, name='generate_qr_code'),
    # path('patient/pdf/<uuid:token>/', generate_pdf_view, name='generate_pdf'),
    path('medical_history/', PatientMedicalRecordListView.as_view(), name='patient_medical_records'),
    path('consultation/<int:appointment_id>/', ConsultationDetailView.as_view(), name='consultation_detail'),
]
