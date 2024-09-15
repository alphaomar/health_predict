from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import Disease
from django.core.exceptions import ValidationError


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
    dosage_form = models.CharField(max_length=100, blank=True, null=True)
    strength = models.CharField(max_length=100, blank=True, null=True)
    indications = models.TextField(blank=True, null=True)
    contraindications = models.TextField(blank=True, null=True)
    side_effects = models.TextField(blank=True, null=True)
    interactions = models.TextField(blank=True, null=True)
    related_diseases = models.ManyToManyField(Disease, blank=True, related_name='drugs')
    availability = models.BooleanField(default=True)
    traditional_medicine_alternative = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    delivery = models.OneToOneField('Delivery', on_delete=models.CASCADE, related_name='order', blank=True, null=True)
    prescriptions = models.ManyToManyField('Prescription', blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    payment_method = models.CharField(max_length=20, choices=[
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ], blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    paypal_order_id = models.CharField(max_length=255, blank=True, null=True)

    # Add these lines
    DELIVERY_CHOICES = [
        ('delivery', 'Delivery'),
        ('pickup', 'Pickup'),
    ]
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_CHOICES, default='delivery')

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"

    def requires_prescription(self):
        return any(item.medication.is_prescription_required for item in self.order_items.all())

    def all_prescriptions_approved(self):
        required_meds = [item.medication for item in self.order_items.all() if item.medication.is_prescription_required]
        approved_prescriptions = self.prescriptions.filter(status='approved', medication__in=required_meds)
        return len(approved_prescriptions) == len(required_meds)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.medication.name} in Order {self.order.id}"


class DeliveryService(models.Model):
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    base_url = models.URLField()

    def __str__(self):
        return self.name


class Delivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    delivery_date = models.DateTimeField(default=timezone.now)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    delivery_notes = models.TextField(blank=True, null=True)
    delivery_service = models.ForeignKey(DeliveryService, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Delivery to {self.address} - Status: {self.status}"

    def update_status(self, new_status):
        self.status = new_status
        if new_status == 'delivered':
            self.actual_delivery_time = timezone.now()
        self.save()

    def get_tracking_info(self):
        if self.delivery_service and self.tracking_number:
            return f"Tracking info for {self.tracking_number} from {self.delivery_service.name}"
        return "No tracking information available"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'medication')

    def __str__(self):
        # Use email or another unique identifier instead of username
        user_identifier = self.user.email if hasattr(self.user, 'email') else str(self.user.id)
        return f"{user_identifier} - {self.medication.name} ({self.quantity})"

    def subtotal(self):
        return self.medication.price * self.quantity

    @property
    def subtotal(self):
        return self.quantity * self.medication.price


class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='prescriptions/')
    upload_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    pharmacist_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='reviewed_prescriptions')
    review_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Prescription for {self.medication.name} - {self.user.username}"


class PharmacyStock(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='stocks')
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, null=True, related_name='stocks')
    quantity = models.PositiveIntegerField()
    last_restock_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pharmacy', 'medication')

    def __str__(self):
        return f"{self.medication.name} at {self.pharmacy.name} - Qty: {self.quantity}"

    def update_stock(self, quantity_change):
        if self.quantity + quantity_change < 0:
            raise ValidationError("Stock cannot be negative.")
        self.quantity += quantity_change
        self.save()

    def restock(self, quantity):
        self.update_stock(quantity)
        self.last_restock_date = timezone.now()
        self.save()
