from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import Disease


class Pharmacy(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    working_hours = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pharmacy_image = models.ImageField(upload_to='pharmacies/', null=True, blank=True)

    def __str__(self):
        return self.name


class Medication(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    is_prescription_required = models.BooleanField(default=False)
    image = models.ImageField(upload_to='medications/', null=True, blank=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    dosage_form = models.CharField(max_length=100, blank=True, null=True)  # e.g., Tablet, Syrup
    strength = models.CharField(max_length=100, blank=True, null=True)  # e.g., 500mg, 10ml
    indications = models.TextField(blank=True, null=True)  # What the drug is used for
    contraindications = models.TextField(blank=True, null=True)  # When not to use the drug
    side_effects = models.TextField(blank=True, null=True)  # Possible side effects
    interactions = models.TextField(blank=True, null=True)  # Drug interactions
    related_diseases = models.ManyToManyField(Disease, blank=True, related_name='drugs')
    availability = models.BooleanField(default=True)  # Track availability
    traditional_medicine_alternative = models.CharField(max_length=255, blank=True, null=True)  # Local alternatives

    def __str__(self):
        return self.name


class PharmacyStock(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='stocks')
    drug = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='stock_entries')
    stock_level = models.PositiveIntegerField()  # Track how many units are available
    restock_date = models.DateField(blank=True, null=True)  # When the pharmacy expects a restock

    def __str__(self):
        return f"{self.drug.name} at {self.pharmacy.name}"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE, related_name='order', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.medication.name} in Order {self.order.id}"


class Delivery(models.Model):
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    delivery_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')

    def __str__(self):
        return f"Delivery to {self.address} - Status: {self.status}"
