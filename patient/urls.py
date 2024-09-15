from django.urls import path
from .views import generate_qr_code_view, generate_pdf_view

urlpatterns = [
    path('patient/qr/<uuid:token>/', generate_qr_code_view, name='generate_qr_code'),
    path('patient/pdf/<uuid:token>/', generate_pdf_view, name='generate_pdf'),
]
