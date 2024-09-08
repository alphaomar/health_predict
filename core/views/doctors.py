from django.views.generic import ListView, DetailView
from django.db.models import Q
from accounts.models import DoctorProfile
from core.models import Disease, Hospital
from django.template.loader import render_to_string


class DoctorListView(ListView):
    model = DoctorProfile
    template_name = 'doctors/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 6  # Number of doctors per page

    def get_queryset(self):
        queryset = DoctorProfile.objects.select_related('user').filter(user__role='doctor', user__is_approved=True)

        query = self.request.GET.get('q')
        specialization = self.request.GET.get('specialization')
        disease_id = self.request.GET.get('disease')
        hospital_id = self.request.GET.get('hospital')

        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(specialization__icontains=query)
            )

        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)

        if disease_id:
            queryset = queryset.filter(disease_specialization__id=disease_id)

        if hospital_id:
            queryset = queryset.filter(hospital__id=hospital_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['specializations'] = DoctorProfile.objects.values_list('specialization', flat=True).distinct()
        context['diseases'] = Disease.objects.all()
        context['hospitals'] = Hospital.objects.all()
        context['selected_specialization'] = self.request.GET.get('specialization', '')
        context['selected_disease'] = self.request.GET.get('disease', '')
        context['selected_hospital'] = self.request.GET.get('hospital', '')
        context['filters_applied'] = any([
            self.request.GET.get('q'),
            self.request.GET.get('specialization'),
            self.request.GET.get('disease'),
            self.request.GET.get('hospital'),
        ])
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('doctors/includes/doctor_list.html', context)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)


class DoctorDetailView(DetailView):
    model = DoctorProfile
    template_name = 'doctors/doctor_detail.html'
    context_object_name = 'doctor'

    def get_queryset(self):
        return DoctorProfile.objects.filter(user__role='doctor', user__is_approved=True).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        # Fetch related doctors based on shared disease specialization
        doctor_diseases = self.object.disease_specialization.all()
        related_doctors = DoctorProfile.objects.filter(
            disease_specialization__in=doctor_diseases
        ).exclude(id=self.object.id).distinct()

        # Fetch reviews for the doctor
        reviews = self.object.reviews.all().order_by('-created_at')

        # Fetch appointments for the doctor
        appointments = self.object.appointments.filter(appointment_status='completed').order_by('-appointment_date')

        # Add the related doctors, reviews, and appointments to the context
        context['related_doctors'] = related_doctors
        context['reviews'] = reviews
        context['appointments'] = appointments

        return context


# views.py
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.http import JsonResponse
from accounts.models import DoctorProfile, Appointment
from core.forms import AppointmentForm

# views.py


# views.py
class CreateAppointmentView(FormView):
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the user to the form
        return kwargs

    def form_valid(self, form):
        doctor = DoctorProfile.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_authenticated:
            # Authenticated user
            patient = self.request.user.patientprofile
            appointment = Appointment(
                doctor=doctor,
                patient=patient,
                appointment_date=form.cleaned_data['appointment_date'],
                appointment_method=form.cleaned_data['appointment_method']
            )
        else:
            # Anonymous user
            name = form.cleaned_data.get('name')
            phone_number = form.cleaned_data.get('phone_number')
            # Create appointment for anonymous user
            appointment = Appointment(
                doctor=doctor,
                appointment_date=form.cleaned_data['appointment_date'],
                appointment_method=form.cleaned_data['appointment_method'],
                anonymous_name=name,
                anonymous_phone=phone_number
            )

        # Save appointment
        appointment.save()

        # Return success response
        return JsonResponse({'status': 'success'}, status=200)

    def form_invalid(self, form):
        # Return form errors in JSON format
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
