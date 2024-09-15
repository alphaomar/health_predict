from .models import Delivery, PharmacyStock

class DeliveryService:
    @staticmethod
    def create_delivery(order):
        return Delivery.objects.create(
            address=order.delivery_address,
            contact_number=order.contact_number,
            order=order
        )

    @staticmethod
    def update_delivery_status(delivery, new_status):
        delivery.update_status(new_status)

class InventoryManagementService:
    @staticmethod
    def update_stock_for_order(order):
        for item in order.order_items.all():
            stock = PharmacyStock.objects.get(pharmacy=order.pharmacy, medication=item.medication)
            stock.update_stock(-item.quantity)

    @staticmethod
    def restock_medication(pharmacy, medication, quantity):
        stock, created = PharmacyStock.objects.get_or_create(pharmacy=pharmacy, medication=medication)
        stock.restock(quantity)