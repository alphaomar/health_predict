from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Pharmacy, Medication, Order, OrderItem, Cart, CartItem, Prescription
from .forms import MedicationForm, OrderForm, PrescriptionForm
from .services import DeliveryService, InventoryManagementService
from django.urls import reverse
import logging
from django.urls import reverse
from django.conf import settings


logger = logging.getLogger(__name__)

class PharmacyListView(ListView):
    model = Pharmacy
    template_name = 'pharmacy/pharmacy_home.html'
    context_object_name = 'pharmacies'

class PharmacyDetailView(DetailView):
    model = Pharmacy
    template_name = 'pharmacy/pharmacy_detail.html'
    context_object_name = 'pharmacy'

class MedicationListView(ListView):
    model = Medication
    template_name = 'pharmacy/medication_list.html'
    context_object_name = 'medications'
    paginate_by = 12  # Adjust as needed

    def get_queryset(self):
        from .forms import MedicationFilterForm  # Import here to avoid circular import

        queryset = Medication.objects.all()
        
        pharmacy_id = self.kwargs.get('pharmacy_id')
        if pharmacy_id:
            self.pharmacy = get_object_or_404(Pharmacy, id=pharmacy_id)
            queryset = queryset.filter(pharmacy=self.pharmacy)
        
        form = MedicationFilterForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            availability = form.cleaned_data.get('availability')

            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search) |
                    Q(generic_name__icontains=search) |
                    Q(brand_name__icontains=search)
                )
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
            if max_price:
                queryset = queryset.filter(price__lte=max_price)
            if availability:
                queryset = queryset.filter(availability=availability == 'True')

        return queryset

    def get_context_data(self, **kwargs):
        from .forms import MedicationFilterForm  # Import here as well

        context = super().get_context_data(**kwargs)
        context['form'] = MedicationFilterForm(self.request.GET)
        if hasattr(self, 'pharmacy'):
            context['pharmacy'] = self.pharmacy
        return context

        
class MedicationDetailView(DetailView):
    model = Medication
    template_name = 'pharmacy/medication_detail.html'
    context_object_name = 'medication'

class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'pharmacy/cart.html'
    context_object_name = 'cart_items'
    paginate_by = 12

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = sum(item.subtotal for item in context['cart_items'])
        return context

def add_to_cart(request, medication_id):
    medication = get_object_or_404(Medication, id=medication_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, medication=medication)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{medication.name} added to cart.")
    cart_count = cart.items.count()
    
    # Redirect to the page the user was on, or to all_medications if referer is not available
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect(reverse('pharmacy:all_medications'))

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    medication_name = cart_item.medication.name
    cart_item.delete()
    messages.success(request, f"{medication_name} removed from cart.")
    return redirect('pharmacy:cart')


# class CheckoutView(LoginRequiredMixin, CreateView):
#     model = Order
#     form_class = OrderForm
#     template_name = 'pharmacy/checkout.html'
#     success_url = reverse_lazy('order_confirmation')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         cart = self.request.user.cart
#         context['cart'] = cart
#         return context

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         order = form.save()
#         cart = self.request.user.cart
#         for item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 medication=item.medication,
#                 quantity=item.quantity,
#                 price=item.medication.price
#             )
#         cart.items.all().delete()
#         DeliveryService.create_delivery(order)
#         InventoryManagementService.update_stock_for_order(order)
#         return super().form_valid(form)


class CheckoutView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'pharmacy/checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.request.user.cart
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.total_amount = self.request.user.cart.total_price

        # Assign a pharmacy to the order
        # You might want to change this logic based on your specific requirements
        default_pharmacy = get_object_or_404(Pharmacy, id=1)  # Assuming you have at least one pharmacy in the database
        form.instance.pharmacy = default_pharmacy

        order = form.save()

        cart = self.request.user.cart
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                medication=item.medication,
                quantity=item.quantity,
                price=item.medication.price
            )

        self.request.session['order_id'] = order.id

        payment_method = self.request.POST.get('payment_method')

        if payment_method == 'stripe':
            return redirect('payment:stripe_payment')
        elif payment_method == 'paypal':
            return redirect('payment:paypal_payment')
        else:
            return redirect('pharmacy:order_confirmation')
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'pharmacy/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'pharmacy/order_detail.html'
    context_object_name = 'order'

class PrescriptionCreateView(LoginRequiredMixin, CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'pharmacy/prescription_create.html'
    success_url = reverse_lazy('prescription_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription
    template_name = 'pharmacy/prescription_list.html'
    context_object_name = 'prescriptions'

    def get_queryset(self):
        return Prescription.objects.filter(user=self.request.user)