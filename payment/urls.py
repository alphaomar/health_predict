


from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('stripe/', views.StripePaymentView.as_view(), name='stripe_payment'),
    path('paypal/', views.PayPalPaymentView.as_view(), name='paypal_payment'),
    path('paypal/capture/', views.PayPalCaptureView.as_view(), name='paypal_capture'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
]