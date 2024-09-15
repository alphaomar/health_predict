
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, DoctorProfile, PharmacistProfile, PatientProfile


@receiver(post_save, sender=CustomUser)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if instance.role == 'doctor':
        DoctorProfile.objects.get_or_create(user=instance)
    elif instance.role == 'pharmacist':
        PharmacistProfile.objects.get_or_create(user=instance)
    elif instance.role == 'patient':
        PatientProfile.objects.get_or_create(user=instance)

    # Save the profile after ensuring it exists
    try:
        if instance.role == 'doctor':
            instance.doctorprofile.save()
        elif instance.role == 'pharmacist':
            instance.pharmacistprofile.save()
        elif instance.role == 'patient':
            instance.patientprofile.save()
    except (DoctorProfile.DoesNotExist, PharmacistProfile.DoesNotExist, PatientProfile.DoesNotExist):
        # Handle case where profile does not exist
        pass
