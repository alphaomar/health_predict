from decimal import Decimal

import paypal
import paypalrestsdk
import requests
import stripe
from paypalrestsdk import Payment
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from pharmacy.models import Order
from payment.models import Payment
from decimal import Decimal
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import logging
import json
from django.utils.safestring import mark_safe
from django.urls import reverse


# create the Stripe instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET
})


class StripePaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'payment/stripe_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        context['stripe_publishable_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def post(self, request, *args, **kwargs):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order, id=order_id)

        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }

        for item in order.order_items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * 100),  # Stripe expects amounts in cents
                    'currency': 'usd',
                    'product_data': {
                        'name': item.medication.name,
                    },
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

def paypal_payment(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('payment:completed')),
                "cancel_url": request.build_absolute_uri(reverse('payment:canceled')),
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": item.product.name,
                        "sku": item.product.id,
                        "price": str(item.price),
                        "currency": "USD",
                        "quantity": item.quantity
                    } for item in order.items.all()]
                },
                "amount": {
                    "total": f"{order.get_total_cost():.2f}",
                    "currency": "SLL"
                },
                "description": f"Order # + {order.id}"
            }]
        })
        if payment.create():
            return redirect(payment.links[1].href)  # Redirect to PayPal approval URL
        else:
            return render(request, 'error.html', {'error': payment.error})
    else:
        return render(request, 'payment/paypal_payment.html', locals())


def payment_completed(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Payment successful
        return render(request, 'success.html')
    else:
        return render(request, 'error.html', {'error': payment.error})


def payment_canceled(request):
    return render(request, 'cancel.html')



class PayPalPaymentView(View):
    def get(self, request):
        order_id = request.session.get('order_id')
        if not order_id:
            return JsonResponse({'error': 'No order ID in session'}, status=400)

        order = get_object_or_404(Order, id=order_id)
        
        order_data = {
            'id': order.id,
            'total': str(order.total_amount),
            # Add any other necessary order data
        }
        
        context = {
            'order': order,
            'client_id': settings.PAYPAL_CLIENT_ID,
            'order_data_json': mark_safe(json.dumps(order_data))
        }
        return render(request, 'payment/paypal_payment.html', context)
    def post(self, request):
        # This method will handle the payment creation
        order_id = request.session.get('order_id')
        if not order_id:
            return JsonResponse({'error': 'No order ID in session'}, status=400)

        order = get_object_or_404(Order, id=order_id)
        
        # Here you would typically create a PayPal order
        # For this example, we'll just return a success response
        return JsonResponse({
            'id': f'PAYPAL-ORDER-ID-{order.id}',
            'status': 'CREATED'
        })

class PayPalCaptureView(View):
    def post(self, request):
        data = json.loads(request.body)
        order_id = request.session.get('order_id')
        paypal_order_id = data.get('paypalOrderID')
        
        if not order_id:
            return JsonResponse({'error': 'No order ID in session'}, status=400)

        order = get_object_or_404(Order, id=order_id)
        
        # Here you would typically verify the payment with PayPal
        # and update your order status
        
        # For this example, we'll just mark the order as paid
        order.paid = True
        order.save()
        
        return JsonResponse({
            'status': 'COMPLETED',
            'order_id': order.id
        })

