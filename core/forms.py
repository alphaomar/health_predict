from django import forms

from accounts.models import Appointment, PatientProfile


class SymptomForm(forms.Form):
    all_symptoms = [
        'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering',
        'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue',
        'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_urination',
        'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings',
        'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat', 'irregular_sugar_level',
        'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration',
        'indigestion', 'headache', 'yellowish_skin', 'dark_urine', 'nausea',
        'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain', 'constipation',
        'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine', 'yellowing_of_eyes',
        'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes',
        'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes',
        'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
        'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region',
        'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps',
        'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes',
        'enlarged_thyroid', 'brittle_nails', 'swollen_extremities', 'excessive_hunger',
        'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech', 'knee_pain',
        'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints',
        'movement_stiffness', 'spinning_movements', 'loss_of_balance', 'unsteadiness',
        'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort',
        'foul_smell_of_urine', 'continuous_feel_of_urine', 'passage_of_gases',
        'internal_itching', 'toxic_look_(typhos)', 'depression', 'irritability', 'muscle_pain',
        'altered_sensorium', 'red_spots_over_body', 'belly_pain', 'abnormal_menstruation',
        'dischromic_patches', 'watering_from_eyes', 'increased_appetite', 'polyuria',
        'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration',
        'visual_disturbances', 'receiving_blood_transfusion', 'receiving_unsterile_injections',
        'coma', 'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption',
        'fluid_overload', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations',
        'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
        'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister',
        'red_sore_around_nose', 'yellow_crust_ooze'
    ]

    symptoms = forms.MultipleChoiceField(
        choices=[(symptom, symptom) for symptom in all_symptoms],
        widget=forms.CheckboxSelectMultiple
    )


# class AppointmentForm(forms.ModelForm):
#     patient_name = forms.CharField(required=False, max_length=100,
#                                    help_text="If patient does not exist, please provide name")
#
#     class Meta:
#         model = Appointment
#         fields = ['doctor', 'patient', 'appointment_date', 'appointment_method', 'appointment_status']
#
#     def clean(self):
#         cleaned_data = super().clean()
#         patient_id = cleaned_data.get('patient')
#         patient_name = cleaned_data.get('patient_name')
#
#         # If patient is not selected, ensure that a name is provided
#         if not patient_id and not patient_name:
#             raise forms.ValidationError("Please provide a patient name if the patient does not exist.")
#
#         return cleaned_data
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         patient_id = self.cleaned_data.get('patient')
#         patient_name = self.cleaned_data.get('patient_name')
#
#         # Create or update patient profile if name is provided and patient_id is not given
#         if not patient_id and patient_name:
#             patient, created = PatientProfile.objects.get_or_create(
#                 user__email=patient_name,  # Assuming email is used as the unique identifier
#                 defaults={'user': None}  # You might need to adjust this based on your actual implementation
#             )
#             instance.patient = patient
#
#         if commit:
#             instance.save()
#         return instance
from django import forms
from accounts.models import Appointment, DoctorProfile, PatientProfile

# forms.py
# forms.py
from django import forms
from accounts.models import Appointment

class AppointmentForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=False, help_text="Required if not logged in.")
    phone_number = forms.CharField(max_length=15, required=False, help_text="Required if not logged in.")

    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_method']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'appointment_method': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Accept the user argument
        super(AppointmentForm, self).__init__(*args, **kwargs)

    # Custom validation to check if name and phone are required for anonymous users
    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not self.user.is_authenticated:
            if not cleaned_data.get('name') or not cleaned_data.get('phone_number'):
                raise forms.ValidationError("Name and phone number are required for anonymous users.")
        return cleaned_data