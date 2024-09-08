from .models import CustomUser, DoctorProfile, PharmacistProfile, PatientProfile
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class DoctorRegistrationForm(UserCreationForm):
    medical_license_number = forms.CharField(required=True, max_length=50)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'medical_license_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.is_active = False  # User remains inactive until admin approval
        user.set_password(self.cleaned_data['password1'])  # Set the hashed password
        if commit:
            user.save()
        return user


class PharmacistRegistrationForm(UserCreationForm):
    license_number = forms.CharField(required=True, max_length=50)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'medical_license_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'pharmacist'
        # user.pharmacy_license_number = self.cleaned_data.get('license_number')
        user.is_active = False  # User remains inactive until admin approval
        if commit:
            user.save()
        return user


class PatientRegistrationForm(UserCreationForm):
    gender = forms.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'gender']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
        return user


class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter Email',
            'class': 'form-control',
            'required': True,
        }),
        label="Email",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control',
            'required': True,
        }),
        label="Password",
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("Invalid email or password.")
            if not user.is_active:
                raise ValidationError("User account is disabled.")
            self.user = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class DoctorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'hospital', 'consultation_fee']


class PharmacistProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PharmacistProfile
        fields = [ 'working_hours', 'services_offered']
