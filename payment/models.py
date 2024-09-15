from django.db import models

class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.payment_method} - {self.amount}"