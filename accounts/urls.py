from django.urls import path
from .views import DoctorRegistrationView, PharmacistRegistrationView, PatientRegistrationView, CustomLoginView, CustomLogoutView

app_name='accounts'
urlpatterns = [
    path('register/doctor/', DoctorRegistrationView.as_view(), name='register_doctor'),
    path('register/pharmacist/', PharmacistRegistrationView.as_view(), name='register_pharmacist'),
    path('register/patient/', PatientRegistrationView.as_view(), name='register_patient'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]
