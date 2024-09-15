from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from accounts.models import ShareableLink, PatientProfile


class MedicalRecordShareView(DetailView):
    model = PatientProfile
    template_name = 'patients/medical_history.html'
    context_object_name = 'patient'

    def get_object(self):
        # Get the token from the URL
        token = self.kwargs.get('token')

        # Retrieve the shareable link or return 404 if not found
        shareable_link = get_object_or_404(ShareableLink, token=token, is_active=True)

        # Check if the link is still valid
        if not shareable_link.is_valid():
            shareable_link.deactivate()
            return HttpResponseForbidden("This link has expired.")

        # Return the patient profile associated with the shareable link
        return shareable_link.patient

    def get_context_data(self, **kwargs):
        # Get the patient object from get_object()
        context = super().get_context_data(**kwargs)

        # Include medical records in the context for display
        context['medical_records'] = self.object.medical_records.all()

        return context


from django.views import View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from accounts.models import PatientProfile


class QRCodeView(View):
    def get(self, request, *args, **kwargs):
        # Get the patient by their email (or use another unique identifier)
        patient = get_object_or_404(PatientProfile, user__email=self.kwargs['email'])

        # Generate QR code for the shareable link
        qr_code_file = patient.generate_qr_code()

        # Serve the QR code image as a response
        response = HttpResponse(qr_code_file, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="{patient.user.email}_qr_code.png"'
        return response


from django.views.generic import View
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from accounts.models import ShareableLink


class MedicalHistoryPDFView(View):
    def get(self, request, *args, **kwargs):
        token = self.kwargs.get('token')
        shareable_link = get_object_or_404(ShareableLink, token=token, is_active=True)

        # Check if the link is valid
        if not shareable_link.is_valid():
            shareable_link.deactivate()
            return HttpResponseForbidden("This link has expired.")

        patient = shareable_link.patient
        medical_records = patient.medical_records.all()

        # Render the template with the medical records
        template = get_template('patients/medical_history_pdf.html')
        html = template.render({'patient': patient, 'medical_records': medical_records})

        # Create a PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="medical_history.pdf"'

        # Generate PDF from HTML
        pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating PDF")

        return response


from django.views.generic import DetailView
from django.shortcuts import get_object_or_404


class PatientProfileView(DetailView):
    model = PatientProfile
    template_name = 'patients/patient_profile.html'
    context_object_name = 'patient'

    def get_object(self):
        return get_object_or_404(PatientProfile, user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qr_code'] = self.object.generate_qr_code()  # QR code image
        context['shareable_link'] = self.object.get_shareable_link()  # Shareable link
        return context
