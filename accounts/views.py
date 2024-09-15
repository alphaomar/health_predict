from .forms import DoctorRegistrationForm, PharmacistRegistrationForm
from django.views.generic import RedirectView
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.contrib import messages, auth
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import CustomLoginForm
from django.urls import reverse_lazy
from django.contrib.auth import login as auth_login
from django.views.generic.edit import CreateView
from .forms import PatientRegistrationForm
from .models import CustomUser

User = get_user_model()


class CustomLoginView(FormView):
    form_class = CustomLoginForm
    template_name = "accounts/login.html"
    success_url = reverse_lazy('core:home')  # Adjust to the appropriate success URL

    def dispatch(self, request, *args, **kwargs):
        # Redirect to success_url if the user is already authenticated
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """If the form is valid, log the user in."""
        user = form.get_user()
        if user is not None:
            auth_login(self.request, user)

            # Add a success message
            messages.success(self.request, f"Welcome back, {user.first_name}!")

            # Redirect to the 'next' parameter if it exists and is safe
            redirect_to = self.request.POST.get('next', self.get_success_url())
            if not url_has_allowed_host_and_scheme(url=redirect_to, allowed_hosts={self.request.get_host()}):
                redirect_to = self.get_success_url()
            return redirect(redirect_to)
        return super().form_invalid(form)

    def form_invalid(self, form):
        """Handle invalid form submissions."""
        # You can customize the invalid form response, like logging or displaying additional error messages.
        messages.error(self.request, "Login failed. Please check your email and password.")
        return super().form_invalid(form)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return self.success_url


class DoctorRegistrationView(CreateView):
    model = CustomUser
    form_class = DoctorRegistrationForm
    template_name = "accounts/doctor_register.html"
    success_url = reverse_lazy('accounts:login')  # Adjust to where you want to redirect after registration

    def form_valid(self, form):
        # Save the form and log in the user
        user = form.save()
        auth_login(self.request, user)
        messages.success(self.request, "Registration successful! You can now update your profile.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle what happens if the form is invalid
        messages.error(self.request, "There was an error with your registration.")
        return super().form_invalid(form)


class PharmacistRegistrationView(CreateView):
    model = CustomUser
    form_class = PharmacistRegistrationForm
    template_name = "accounts/pharmacist_register.html"
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Save the form and log in the user
        user = form.save()
        auth_login(self.request, user)
        messages.success(self.request, "Registration successful! You can now update your profile.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle what happens if the form is invalid
        messages.error(self.request, "There was an error with your registration.")
        return super().form_invalid(form)


class PatientRegistrationView(CreateView):
    model = CustomUser
    form_class = PatientRegistrationForm
    template_name = "accounts/patient_register.html"
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        # Save the form and log in the user
        user = form.save()
        auth_login(self.request, user)
        messages.success(self.request, "Registration successful! You can now update your profile.")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle what happens if the form is invalid
        messages.error(self.request, "There was an error with your registration.")
        return super().form_invalid(form)


class CustomLogoutView(RedirectView):
    url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        messages.success(request, "You have been logged out.")
        return super().get(request, *args, **kwargs)
