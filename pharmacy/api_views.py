# pharmacy/api_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Medication, Pharmacy, Order, Prescription
from .serializers import MedicationSerializer, PharmacySerializer, OrderSerializer, PrescriptionSerializer

class MedicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsAuthenticated]

class PharmacyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Prescription.objects.filter(user=self.request.user)