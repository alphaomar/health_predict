from django.contrib import admin
from .models import (
    Pharmacy, Medication, Order, OrderItem, DeliveryService, Delivery,
    Cart, CartItem, Prescription, PharmacyStock
)

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number', 'email')
    search_fields = ('name', 'address', 'email')

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'pharmacy', 'price', 'stock_quantity', 'is_prescription_required', 'availability')
    list_filter = ('pharmacy', 'is_prescription_required', 'availability')
    search_fields = ('name', 'generic_name', 'brand_name')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pharmacy', 'total_amount', 'order_date', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('user__email', 'pharmacy__name')
    inlines = [OrderItemInline]

@admin.register(DeliveryService)
class DeliveryServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url')

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('address', 'contact_number', 'delivery_date', 'status', 'tracking_number')
    list_filter = ('status',)
    search_fields = ('address', 'tracking_number')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'total_price')
    search_fields = ('user__email',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'medication', 'quantity', 'added_at', 'subtotal')
    list_filter = ('added_at',)
    search_fields = ('cart__user__email', 'medication__name')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'medication', 'upload_date', 'expiry_date', 'status')
    list_filter = ('status', 'upload_date', 'expiry_date')
    search_fields = ('user__email', 'medication__name')

@admin.register(PharmacyStock)
class PharmacyStockAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'medication', 'quantity', 'last_restock_date')
    list_filter = ('last_restock_date',)
    search_fields = ('pharmacy__name', 'medication__name')