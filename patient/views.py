from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from accounts.models import PatientProfile


def generate_qr_code_view(request, token):
    patient_profile = get_object_or_404(PatientProfile, shareable_token=token)
    qr_code = patient_profile.generate_qr_code()

    response = HttpResponse(qr_code, content_type="image/png")
    response['Content-Disposition'] = f'inline; filename="{patient_profile.user.email}_qr_code.png"'
    return response


# from weasyprint import HTML
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from accounts.models import PatientProfile
#
#
# def generate_pdf_view(request, token):
#     # Get patient profile using token
#     patient_profile = get_object_or_404(PatientProfile, shareable_token=token)
#
#     # Render the HTML content
#     html_content = render_to_string('patients/shared_profile.html', {'patient_profile': patient_profile})
#
#     # Convert HTML to PDF using WeasyPrint
#     html = HTML(string=html_content)
#     pdf = html.write_pdf()
#
#     # Serve the PDF as a download response
#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename="{patient_profile.user.email}_profile.pdf"'
#     return response
#

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from accounts.models import Consultation, Appointment


# Create your views here.

class PatientMedicalRecordListView(LoginRequiredMixin, ListView):
    model = Consultation
    template_name = 'dashboard/patient/medical_records_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(patient__user=self.request.user)


class ConsultationDetailView(LoginRequiredMixin, DetailView):
    model = Consultation
    template_name = 'dashboard/patient/consultation_detail.html'
    context_object_name = 'consultation'

    def get_object(self):
        appointment = get_object_or_404(Appointment, id=self.kwargs['appointment_id'], patient__user=self.request.user)
        return get_object_or_404(Consultation, appointment=appointment)
