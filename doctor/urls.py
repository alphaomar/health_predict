from django.urls import path

from ai_chat.urls import app_name
from .views import (DoctorReportTemplateView, DoctorAppointmentListView, DoctorMedicalRecordsListView,

                    DoctorPatientListView, DoctorConsultationListView, DoctorPrescriptionListView,
                    DoctorAvailabilityListView, DoctorPendingAppointment, DoctorCancelledAppointment,
                    DoctorCompletedAppointment, DoctorRegisterPatientView, DoctorPatientDetailView,
                    PatientMedicalRecordDetailView, PatientProfileUpdateView, PatientProfileDeleteView,
                    PatientMedicalRecordUpdateView, PatientMedicalRecordDeleteView, AppointmentCreateView,
                    AppointmentUpdateView, AppointmentDeleteView, PrescriptionCreateView, PrescriptionDeleteView,
                    PrescriptionUpdateView, ConsultationCreateView, ConsultationUpdateView, ConsultationDeleteView,
                    PrescriptionDetailView, ConsultationDetailView,
                   )
app_name='doctor'
urlpatterns = [
    path('', DoctorReportTemplateView.as_view(), name='doctor_report'),
    path('doctor/appointments/', DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    path('medical/record/', DoctorMedicalRecordsListView.as_view(), name='medical_records'),
    path('patient/listview/', DoctorPatientListView.as_view(), name='patient_list'),
    path('/consulation-view/', DoctorConsultationListView.as_view(), name='consultation_index'),
    path('prescriptions/', DoctorPrescriptionListView.as_view(), name='doctor-prescriptions'),
    path('availiability/', DoctorAvailabilityListView.as_view(), name='availability'),
    path('pending/appointment/', DoctorPendingAppointment.as_view(), name='pending_appointments'),
    path('completed/appointment/', DoctorCompletedAppointment.as_view(), name='completed_appointments'),
    path('cancelled/appointment/', DoctorCancelledAppointment.as_view(), name='cancelled_appointments'),
    path('patients/add/', DoctorRegisterPatientView.as_view(), name='patient-create'),
    path('patient-detail/<int:pk>/', DoctorPatientDetailView.as_view(), name='doctor_patient_detail'),
    path('medical-record_detail/<int:pk>/', PatientMedicalRecordDetailView.as_view(), name='patient_medical_records'),
    path('patient/<int:pk>/update/', PatientProfileUpdateView.as_view(), name='update_patient_profile'),
    path('patient/<int:pk>/delete/', PatientProfileDeleteView.as_view(), name='delete_patient_profile'),
    path('patient-medical-records/<int:pk>/update/', PatientMedicalRecordUpdateView.as_view(),
         name='update_patient_medical_records'),
    path('patient-medical-records/<int:pk>/delete/', PatientMedicalRecordDeleteView.as_view(),
         name='delete_patient_medical_records'),
    path('create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('/<int:pk>/update/', AppointmentUpdateView.as_view(), name='appointment_update'),
    path('/<int:pk>/delete/', AppointmentDeleteView.as_view(), name='appointment_delete'),

    path('prescription/add/', PrescriptionCreateView.as_view(), name='add_prescription'),
    path('prescription/<int:pk>/update/', PrescriptionUpdateView.as_view(), name='update_prescription'),
    path('prescription/<int:pk>/delete/', PrescriptionDeleteView.as_view(), name='delete_prescription'),

    path('consultation/add/', ConsultationCreateView.as_view(), name='add_consultation'),
    path('consultation/<int:pk>/update/', ConsultationUpdateView.as_view(), name='update_consultation'),
    path('consultation/<int:pk>/delete/', ConsultationDeleteView.as_view(), name='delete_consultation'),

    path('prescription/<int:pk>/', PrescriptionDetailView.as_view(), name='prescription_detail'),

    path('consultation/<int:pk>/', ConsultationDetailView.as_view(), name='consultation_detail'),

    # path('availability/create/', AvailabilityCreateView.as_view(), name='availability_create'),
    # path('availability/<int:pk>/update/', AvailabilityUpdateView.as_view(), name='availability_update'),
    # path('availability/<int:pk>/delete/', AvailabilityDeleteView.as_view(), name='availability_delete'),

]
