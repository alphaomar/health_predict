import uuid
from io import BytesIO

import qrcode
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.conf import settings
from core.models import Disease, Hospital
from pharmacy.models import Pharmacy, Medication


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('pharmacist', 'Pharmacist'),
        ('patient', 'Patient'),
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
    medical_license_number = models.CharField(max_length=50, blank=True, null=True)
    pharmacy_license_number = models.CharField(max_length=50, blank=True, null=True)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    objects = CustomUserManager()


class BaseProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True


class BaseProfessionalProfile(BaseProfile):
    years_of_experience = models.IntegerField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    languages_spoken = models.ManyToManyField('Language', blank=True)

    class Meta:
        abstract = True


class DoctorProfile(BaseProfessionalProfile):
    specialization = models.CharField(max_length=100, blank=True, null=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    disease_specialization = models.ManyToManyField(Disease, blank=True)
    pharmacies = models.ManyToManyField(Pharmacy, blank=True)
    # Doctor-specific KPIs
    total_patients = models.IntegerField(default=0)
    total_appointments = models.IntegerField(default=0)
    total_consultation_fees = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    last_appointment_date = models.DateTimeField(blank=True, null=True)
    room_name = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def update_rating(self):
        reviews = self.reviews.all()
        self.total_reviews = reviews.count()
        self.average_rating = sum(
            [review.rating for review in reviews]) / self.total_reviews if self.total_reviews > 0 else 0.0
        self.save()

    def __str__(self):
        return f"{self.user.email}'s Doctor Profile"


class PatientProfile(BaseProfile):
    shareable_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    gender = models.CharField(max_length=10, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)
    immunizations = models.TextField(blank=True, null=True)
    primary_care_physician = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)

    # Many-to-many relationship with doctors
    doctors = models.ManyToManyField('DoctorProfile', through='Appointment', related_name='patients')

    def generate_qr_code(self):
        """Generate a QR code for the shareable link."""
        shareable_link = self.get_shareable_link()  # Get the shareable URL for the patient

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(shareable_link)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Save the image in memory
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)

        return File(buffer, name=f'{self.user.email}_qr_code.png')

    def create_shareable_link(self, validity_minutes=60):
        """Create a shareable link that expires after a certain time."""
        expiration_time = timezone.now() + timedelta(minutes=validity_minutes)
        shareable_link = ShareableLink.objects.create(
            patient=self,
            expires_at=expiration_time,
        )
        return f"{settings.BASE_URL}/patient/share/{shareable_link.token}/"

    def get_shareable_link(self):
        """Get or create a new shareable link."""
        shareable_link = ShareableLink.objects.filter(patient=self, is_active=True).last()
        if shareable_link and shareable_link.is_valid():
            return f"{settings.BASE_URL}/patient/share/{shareable_link.token}/"
        else:
            return self.create_shareable_link()  # Create a new link if no valid one exists

    def __str__(self):
        return f"{self.user.email}'s Patient Profile"


class PharmacistProfile(BaseProfessionalProfile):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, blank=True, null=True)
    working_hours = models.TextField(blank=True, null=True)
    services_offered = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email}'s Pharmacist Profile"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='medical_records')
    diagnosis = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_of_visit = models.DateTimeField(default=timezone.now)
    follow_up_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Medical Record of {self.patient.user.email} on {self.date_of_visit}"


class Prescription(models.Model):
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='prescriptions', blank=True,
                                   null=True)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    prescribed_by = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='prescriptions')
    date_prescribed = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Prescription for {self.medication_name} to {self.medical_record.patient.user.email}"


class Consultation(models.Model):
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE, related_name='consultation')
    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    treatment_plan = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    consultation_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Consultation for {self.appointment.patient.user.email} on {self.consultation_date}"


from django.utils import timezone
from datetime import timedelta


class ShareableLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='shareable_links')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Time of expiration
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        """Check if the link is still valid."""
        return self.is_active and timezone.now() < self.expires_at

    def deactivate(self):
        """Mark the link as inactive."""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"Shareable link for {self.patient.user.email} (expires at {self.expires_at})"


class Availability(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availabilities')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Enforce UTC timezone before saving
        if self.start_time.tzinfo is None:
            self.start_time = timezone.make_aware(self.start_time, timezone.utc)
        if self.end_time.tzinfo is None:
            self.end_time = timezone.make_aware(self.end_time, timezone.utc)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor.user.email} available from {self.start_time} to {self.end_time}"


class Appointment(models.Model):
    APPOINTMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In Person'),
    ]
    APPOINTMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments', null=True,
                                blank=True)
    appointment_date = models.DateTimeField()
    appointment_method = models.CharField(max_length=20, choices=APPOINTMENT_METHOD_CHOICES, null=True, blank=True)
    appointment_status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default='pending')
    fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    anonymous_name = models.CharField(max_length=100, blank=True, null=True)
    anonymous_phone = models.CharField(max_length=15, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-populate consultation fee if not provided
        if not self.fee_paid:
            self.fee_paid = self.doctor.consultation_fee or 0.00
        super().save(*args, **kwargs)

        # Update doctor KPIs on appointment completion
        if self.appointment_status == 'completed':
            doctor_profile = self.doctor
            doctor_profile.total_appointments += 1
            doctor_profile.total_consultation_fees += self.fee_paid
            doctor_profile.last_appointment_date = self.appointment_date
            doctor_profile.total_patients = doctor_profile.appointments.values('patient').distinct().count()
            doctor_profile.save()

    def __str__(self):
        return f"Appointment with {self.doctor} for {self.patient} on {self.appointment_date}"


class Review(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'patient')  # Prevent duplicate reviews by the same patient

    def __str__(self):
        return f"Review by {self.patient.user.email} for {self.doctor.user.email} - {self.rating} stars"


class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
