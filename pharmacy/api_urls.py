# pharmacy/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import MedicationViewSet, PharmacyViewSet, OrderViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r'medications', MedicationViewSet)
router.register(r'pharmacies', PharmacyViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
]