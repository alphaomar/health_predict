from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, UpdateView
from accounts.mixins import DoctorRequiredMixin, PatientRequiredMixin
from accounts.models import DoctorProfile, PatientProfile
from accounts.forms import DoctorProfileUpdateForm
from django.urls import reverse_lazy
# Create your views here.


class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'dashboard/doctor/index.html'


class DoctorProfileDetailView(DoctorRequiredMixin, DetailView):
    model = DoctorProfile
    template_name = 'dashboard/doctor/detail.html'
    context_object_name = 'doctor'


class PatientDashboard(PatientRequiredMixin, TemplateView):
    template_name = 'dashboard/patient/index.html'


class PatientProfileDetailView(PatientRequiredMixin, DetailView):

    model = PatientProfile
    template_name = 'dashboard/patient/detail.html'
    context_object_name = 'patient'


class DoctorUpdateView(UpdateView):
    model = DoctorProfile
    template_name = 'dashboard/doctor/update.html'
    form_class = DoctorProfileUpdateForm
    success_url = reverse_lazy('doctors-profile')












