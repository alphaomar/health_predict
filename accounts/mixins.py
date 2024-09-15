from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views import View


class RoleRequiredMixin(View):
    role_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if self.role_required and request.user.role != self.role_required:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DoctorRequiredMixin(RoleRequiredMixin):
    role_required = 'doctor'


class PharmacistRequiredMixin(RoleRequiredMixin):
    role_required = 'pharmacist'


class PatientRequiredMixin(RoleRequiredMixin):
    role_required = 'patient'
