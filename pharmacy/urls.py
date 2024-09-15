from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.PharmacyListView.as_view(), name='pharmacy_list'),
    path('pharmacy/<int:pk>/', views.PharmacyDetailView.as_view(), name='pharmacy_detail'),
    path('medications/', views.MedicationListView.as_view(), name='all_medications'),
    path('pharmacy/<int:pharmacy_id>/medications/', views.MedicationListView.as_view(), name='pharmacy_medications'),
    path('medication/<int:pk>/', views.MedicationDetailView.as_view(), name='medication_detail'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
     path('pharmacy/<int:pharmacy_id>/medications/', views.MedicationListView.as_view(), name='pharmacy_medications'),



    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:medication_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('prescription/create/', views.PrescriptionCreateView.as_view(), name='prescription_create'),
    path('prescriptions/', views.PrescriptionListView.as_view(), name='prescription_list'),
]