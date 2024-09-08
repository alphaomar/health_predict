from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DoctorProfile, PharmacistProfile, PatientProfile, Review, Appointment


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'is_approved')
    list_filter = ('role', 'is_staff', 'is_active', 'is_approved')

    # Define fields to display and edit in the admin form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_approved', 'role')}),
    )

    # Define fields to display when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active', 'is_approved',
            'role')}
         ),
    )

    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DoctorProfile)
admin.site.register(PharmacistProfile)
admin.site.register(PatientProfile)
admin.site.register(Appointment)
admin.site.register(Review)
