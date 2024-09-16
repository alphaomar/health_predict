from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, DeleteView, UpdateView, CreateView, DetailView
from accounts.models import (DoctorProfile, Appointment, Review, MedicalRecord,
                             PatientProfile, Consultation, \
                             Prescription, Availability)
from accounts.mixins import DoctorRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from doctor.forms import PatientProfileForm, CustomUserCreationForm, PatientProfileUpdateForm, \
    PatientMedicalRecordUpdateForm, AppointmentForm, PrescriptionForm, ConsultationForm, AvailabilityForm


# Create your views here.

class DoctorAppointmentListView(DoctorRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/doctor_appointment_index.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)

        return Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')


class DoctorPendingAppointment(DoctorRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/pending_appointment.html'
    context_object_name = 'pending_appointments'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        return Appointment.objects.filter(doctor=doctor, appointment_status='pending')


class DoctorCompletedAppointment(DoctorRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/completed_appointments.html'
    context_object_name = 'completed_appointments'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)

        return Appointment.objects.filter(doctor=doctor, appointment_status='completed')


class DoctorCancelledAppointment(DoctorRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/cancelled_appointment.html'
    context_object_name = 'cancelled_appointments'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        return Appointment.objects.filter(doctor=doctor, appointment_status='cancelled')


class DoctorReportTemplateView(DoctorRequiredMixin, TemplateView):
    template_name = 'dashboard/doctor/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        doctor = get_object_or_404(DoctorProfile, user=self.request.user)

        appointments = Appointment.objects.filter(doctor=doctor)

        context['total_appointments'] = appointments.count()

        context['pending_appointments'] = appointments.filter(appointment_status='pending').count()
        context['completed_appointments'] = appointments.filter(appointment_status='completed').count()
        context['cancelled_appointments'] = appointments.filter(appointment_status='cancelled').count()

        context['online_appointments'] = appointments.filter(appointment_method='online').count()
        context['in_person_appointments'] = appointments.filter(appointment_method='in_person').count()

        context['total_fees_collected'] = \
            appointments.filter(appointment_status='completed').aggregate(Sum('fee_paid'))['fee_paid__sum'] or 0
        context['average_fee'] = appointments.filter(appointment_status='completed').aggregate(Avg('fee_paid'))[
                                     'fee_paid__avg'] or 0

        reviews = Review.objects.filter(doctor=doctor)
        context['total_reviews'] = reviews.count()
        context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        context['five_star_reviews'] = reviews.filter(rating=5).count()
        context['four_star_reviews'] = reviews.filter(rating=4).count()
        context['three_star_reviews'] = reviews.filter(rating=3).count()
        context['two_star_reviews'] = reviews.filter(rating=2).count()
        context['one_star_reviews'] = reviews.filter(rating=1).count()

        return context


class DoctorMedicalRecordsListView(DoctorRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'dashboard/doctor/medical_records.html'
    context_object_name = 'medical_records'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        return MedicalRecord.objects.filter(doctor=doctor)


class DoctorPatientListView(DoctorRequiredMixin, ListView):
    model = PatientProfile
    template_name = 'dashboard/doctor/patient_list.html'
    context_object_name = 'patients'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        return PatientProfile.objects.filter(doctors=doctor)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctor'] = get_object_or_404(DoctorProfile, user=self.request.user)
        return context


class DoctorConsultationListView(DoctorRequiredMixin, ListView):
    model = Consultation
    template_name = 'dashboard/doctor/consultation.html'
    context_object_name = 'consultations'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)

        return Consultation.objects.filter(appointment__doctor=doctor).order_by('-consultation_date')


class DoctorPrescriptionListView(DoctorRequiredMixin, ListView):
    model = Prescription
    template_name = 'dashboard/doctor/prescriptions_list.html'
    context_object_name = 'prescriptions'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)

        return Prescription.objects.filter(prescribed_by=doctor).order_by('-date_prescribed')


class DoctorAvailabilityListView(DoctorRequiredMixin, ListView):
    model = Availability
    template_name = 'dashboard/doctor/availability.html'
    context_object_name = 'availabilities'

    def get_queryset(self):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)

        return Availability.objects.filter(doctor=doctor)


class DoctorRegisterPatientView(View):
    def get(self, request):
        user_form = CustomUserCreationForm()
        profile_form = PatientProfileForm()
        return render(request, 'dashboard/doctor/add_patient.html', {
            'user_form': user_form,
            'profile_form': profile_form,
        })

    @transaction.atomic
    def post(self, request):
        user_form = CustomUserCreationForm(request.POST)
        profile_form = PatientProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'patient'
            user.save()

            # Ensure the user doesn't already have a patient profile
            if not PatientProfile.objects.filter(user=user).exists():

                patient_profile = profile_form.save(commit=False)
                patient_profile.user = user
                patient_profile.save()

                messages.success(request, 'Patient successfully registered.')
                return redirect('doctor_dashboard')  # Replace with your dashboard URL
            else:
                messages.error(request, 'This user already has a patient profile.')

        return render(request, 'dashboard/doctor/add_patient.html', {
            'user_form': user_form,
            'profile_form': profile_form,
        })


class DoctorPatientDetailView(DoctorRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'dashboard/doctor/patient_detail.html'
    context_object_name = 'patient'


class PatientMedicalRecordDetailView(DetailView):
    model = MedicalRecord
    template_name = 'dashboard/doctor/patient_medical_record_detail.html'
    context_object_name = 'medical_records'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = self.object.patient
        return context


class PatientProfileUpdateView(DoctorRequiredMixin, UpdateView):
    model = PatientProfile
    form_class = PatientProfileUpdateForm
    template_name = 'dashboard/doctor/update_patient_profile.html'

    def get_success_url(self):
        return reverse_lazy('doctor_patient_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        patient_id = self.kwargs.get('pk')
        return get_object_or_404(PatientProfile, pk=patient_id)


class PatientProfileDeleteView(DeleteView):
    model = PatientProfile
    template_name = 'dashboard/doctor/delete_patient_profile.html'
    success_url = reverse_lazy('patient_list')

    def get_object(self, queryset=None):
        patient_id = self.kwargs.get('pk')
        return get_object_or_404(PatientProfile, pk=patient_id)


class PatientMedicalRecordUpdateView(DoctorRequiredMixin, UpdateView):
    model = MedicalRecord
    form_class = PatientMedicalRecordUpdateForm
    template_name = 'dashboard/doctor/medical_records_update.html'

    def get_success_url(self):
        return reverse_lazy('patient_medical_records', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        patient_id = self.kwargs.get('pk')
        return get_object_or_404(MedicalRecord, pk=patient_id)


class PatientMedicalRecordDeleteView(DeleteView):
    model = MedicalRecord
    template_name = 'dashboard/doctor/medical_record_delete.html'
    success_url = reverse_lazy('medical_records')

    def get_object(self, queryset=None):
        patient_id = self.kwargs.get('pk')
        return get_object_or_404(MedicalRecord, pk=patient_id)


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create_appointment.html'

    def form_valid(self, form):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        form.instance.doctor = doctor
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['doctor'] = get_object_or_404(DoctorProfile, user=self.request.user)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('doctor:doctor_appointments')


class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create_appointment.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the doctor to the form
        kwargs['doctor'] = get_object_or_404(DoctorProfile, user=self.request.user)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('doctor_appointments')


class AppointmentDeleteView(DoctorRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('doctor_appointments')


class PrescriptionCreateView(DoctorRequiredMixin, CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'dashboard/doctor/prescription_form.html'

    def form_valid(self, form):
        form.instance.prescribed_by = self.request.user.doctorprofile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('patient_medical_records', kwargs={'pk': self.object.medical_record.pk})


class PrescriptionUpdateView(DoctorRequiredMixin, UpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'dashboard/doctor/prescription_form.html'

    def form_valid(self, form):
        form.instance.prescribed_by = self.request.user.doctorprofile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('patient_medical_records', kwargs={'pk': self.object.medical_record.pk})


class PrescriptionDeleteView(DoctorRequiredMixin, DeleteView):
    model = Prescription
    template_name = 'dashboard/doctor/prescription_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('patient_medical_records', kwargs={'pk': self.object.medical_record.pk})


class ConsultationCreateView(LoginRequiredMixin, CreateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'dashboard/doctor/consultation_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['doctor'] = self.request.user.doctorprofile
        return kwargs

    def get_success_url(self):
        return reverse_lazy('doctor:consultation_index')


class ConsultationUpdateView(LoginRequiredMixin, UpdateView):
    model = Consultation
    form_class = ConsultationForm
    template_name = 'dashboard/doctor/consultation_form.html'

    def get_success_url(self):
        return reverse_lazy('consultation_index')


class ConsultationDeleteView(LoginRequiredMixin, DeleteView):
    model = Consultation
    template_name = 'dashboard/doctor/consultation_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('consultation_index')


class PrescriptionDetailView(DetailView):
    model = Prescription
    template_name = 'dashboard/doctor/prescription_detail.html'
    context_object_name = 'prescription'

    def get_queryset(self):
        # Limiting the prescriptions shown to those prescribed by the logged-in doctor
        return Prescription.objects.filter(prescribed_by=self.request.user.doctorprofile)


class ConsultationDetailView(DetailView):
    model = Consultation
    template_name = 'dashboard/doctor/consultation_detail.html'
    context_object_name = 'consultation'

    def get_queryset(self):
        # Limit the consultations shown to those conducted by the logged-in doctor
        return Consultation.objects.filter(appointment__doctor=self.request.user.doctorprofile)


'''

class AvailabilityCreateView(LoginRequiredMixin, CreateView):
    model = Availability
    form_class = AvailabilityForm
    template_name = 'dashboard/doctor/availability_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the doctor to the form
        kwargs['doctor'] = get_object_or_404(DoctorProfile, user=self.request.user)
        return kwargs

    def get_success_url(self):
        return reverse_lazy('availability')


class AvailabilityUpdateView(LoginRequiredMixin, UpdateView):
    model = Availability
    form_class = AvailabilityForm
    template_name = 'dashboard/doctor/availability_form.html'



class AvailabilityDeleteView(LoginRequiredMixin, DeleteView):
    model = Availability
    template_name = 'dashboard/doctor/availability_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('availability')
'''
