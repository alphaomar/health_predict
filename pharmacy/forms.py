from django import forms
from .models import Medication, Order, Prescription, Pharmacy

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'description', 'price', 'stock_quantity', 'is_prescription_required', 'image', 'generic_name', 'brand_name', 'dosage_form', 'strength', 'indications', 'contraindications', 'side_effects', 'interactions', 'related_diseases', 'availability', 'traditional_medicine_alternative']

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['delivery_method']
#         widgets = {
#             'delivery_method': forms.RadioSelect(attrs={'disabled': 'disabled'}),
#             'payment_method': forms.RadioSelect,
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['delivery_address'] = forms.CharField(
#             max_length=255, 
#             required=False, 
#             widget=forms.TextInput(attrs={'readonly': 'readonly'})
#         )
#         self.fields['contact_number'] = forms.CharField(
#             max_length=15, 
#             required=True  # Changed to required
#         )
#         # Set a default value for delivery_method
#         self.initial['delivery_method'] = 'pickup'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_method']
        widgets = {
            'payment_method': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_address'] = forms.CharField(max_length=255, required=False, disabled=True)
        self.fields['contact_number'] = forms.CharField(max_length=15, required=True)

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get('delivery_method')
        delivery_address = cleaned_data.get('delivery_address')
        contact_number = cleaned_data.get('contact_number')

        if delivery_method == 'delivery' and not delivery_address:
            self.add_error('delivery_address', "Delivery address is required for delivery orders.")

        if not contact_number:
            self.add_error('contact_number', "Contact number is required.")

        return cleaned_data

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication', 'image', 'expiry_date']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MedicationFilterForm(forms.Form):
    search = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    availability = forms.ChoiceField(choices=[('', 'All'), (True, 'Available'), (False, 'Not Available')], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})