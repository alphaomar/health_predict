# pharmacy/serializers.py
from rest_framework import serializers
from .models import Medication, Pharmacy, Order, Prescription

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id', 'name', 'address', 'contact_number', 'email']

class MedicationSerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer(read_only=True)

    class Meta:
        model = Medication
        fields = ['id', 'name', 'description', 'price', 'pharmacy', 'is_prescription_required']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'pharmacy', 'total_amount', 'status', 'order_date']

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'user', 'medication', 'image', 'expiry_date', 'status']