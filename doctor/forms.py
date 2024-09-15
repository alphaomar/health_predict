# forms.py

from django import forms
from accounts.models import CustomUser, PatientProfile, MedicalRecord, Appointment, Prescription, Consultation, \
    Availability
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus.widgets import DatePickerInput


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['gender', 'medical_history', 'allergies', 'chronic_conditions', 'family_history', 'immunizations',
                  'primary_care_physician', 'emergency_contact_name', 'emergency_contact_phone']


class PatientProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = [
            'medical_history', 'allergies', 'chronic_conditions',
            'family_history', 'immunizations', 'primary_care_physician',
            'emergency_contact_name', 'emergency_contact_phone'
        ]


class PatientMedicalRecordUpdateForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'diagnosis', 'symptoms', 'notes', 'date_of_visit', 'follow_up_date'
        ]


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'appointment_date', 'appointment_method', 'appointment_status', 'fee_paid']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            # You can add other widgets here if needed
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

        # Show only registered patients in the dropdown
        self.fields['patient'].queryset = PatientProfile.objects.all()

        # Hide the doctor field in the form as it will be auto-assigned
        if doctor:
            self.instance.doctor = doctor


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medical_record', 'medication', 'dosage', 'frequency', 'duration']


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['appointment', 'symptoms', 'diagnosis', 'treatment_plan', 'doctor_notes']

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)

        # Filter appointments to show only those related to the logged-in doctor
        if doctor:
            self.fields['appointment'].queryset = Appointment.objects.filter(doctor=doctor)


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['start_time', 'end_time']  # No doctor field, only start and end time

    widgets = {
        'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    }
