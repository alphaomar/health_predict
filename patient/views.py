from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from accounts.models import PatientProfile


def generate_qr_code_view(request, token):
    patient_profile = get_object_or_404(PatientProfile, shareable_token=token)
    qr_code = patient_profile.generate_qr_code()

    response = HttpResponse(qr_code, content_type="image/png")
    response['Content-Disposition'] = f'inline; filename="{patient_profile.user.email}_qr_code.png"'
    return response


from weasyprint import HTML
from django.template.loader import render_to_string
from django.http import HttpResponse
from accounts.models import PatientProfile


def generate_pdf_view(request, token):
    # Get patient profile using token
    patient_profile = get_object_or_404(PatientProfile, shareable_token=token)

    # Render the HTML content
    html_content = render_to_string('patients/shared_profile.html', {'patient_profile': patient_profile})

    # Convert HTML to PDF using WeasyPrint
    html = HTML(string=html_content)
    pdf = html.write_pdf()

    # Serve the PDF as a download response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{patient_profile.user.email}_profile.pdf"'
    return response
