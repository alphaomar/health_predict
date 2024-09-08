import numpy as np
import pickle
import tensorflow as tf
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from core.forms import SymptomForm
import google.generativeai as genai
import markdown2

from core.models import Disease


class DiseasePredictionView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load the trained model and label encoder
        self.model = tf.keras.models.load_model(settings.MODEL_PATH)
        with open(settings.LABEL_ENCODER_PATH, 'rb') as f:
            self.label_encoder = pickle.load(f)
        # Define the complete list of symptoms/features used during training
        self.all_symptoms = [
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

    def get(self, request, *args, **kwargs):
        form = SymptomForm()
        return render(request, 'core/predict_disease.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = SymptomForm(request.POST)
        if form.is_valid():
            symptoms = form.cleaned_data['symptoms']
            input_vector = self.create_symptom_vector(symptoms)

            # Ensure the input vector length matches the number of symptoms
            if len(input_vector) != len(self.all_symptoms):
                return JsonResponse({'error': 'Input vector length mismatch'}, status=400)

            input_vector = np.array([input_vector])
            y_pred = self.model.predict(input_vector)

            predicted_class = np.argmax(y_pred, axis=1)[0]
            predicted_disease_name = self.label_encoder.inverse_transform([predicted_class])[0]
            predicted_probability = y_pred[0][predicted_class]

            # Integrate Gemini AI to get detailed disease information with probability
            disease_info_html = self.get_disease_information(predicted_disease_name, predicted_probability)

            # Fetch doctors specializing in the predicted disease
            disease = Disease.objects.filter(name__icontains=predicted_disease_name).first()
            doctors = disease.doctorprofile_set.all() if disease else []

            return render(request, 'core/prediction_result.html', {
                'predicted_disease': predicted_disease_name,
                'predicted_probability': predicted_probability,
                'disease_information': disease_info_html,
                'doctors': doctors,
            })
        return render(request, 'core/predict_disease.html', {'form': form})

    def create_symptom_vector(self, symptom_names):
        symptom_vector = [0] * len(self.all_symptoms)
        for symptom in symptom_names:
            if symptom in self.all_symptoms:
                index = self.all_symptoms.index(symptom)
                symptom_vector[index] = 1
        return symptom_vector

    def get_disease_information(self, disease, probability):
        genai.configure(api_key='AIzaSyASefeu3w7RpGKJZGRzEcsyjFJ9wv2rv7A')
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Please provide a detailed explanation about {disease}. The predicted probability for this disease is {probability:.2%}. 
        The information should be structured as follows:

        1. **Overview**: Provide a brief introduction to the disease.
        2. **Causes**: Explain the causes and risk factors associated with the disease.
        3. **Symptoms**: Describe the common symptoms experienced by patients.
        4. **Diagnosis**: Outline the diagnostic methods used by healthcare professionals to identify the disease.
        5. **Treatment**: Discuss the available treatments, including medications, therapies, and any surgical options. Specify treatment recommendations for different stages of the disease.
        6. **Prevention**: Suggest preventive measures that can reduce the risk of developing the disease.
        7. **Management**: Offer advice on managing the disease in daily life, including lifestyle changes and supportive care.
        8. **Prognosis**: Provide information on the likely course and outcome of the disease, including factors that influence prognosis.
        9. **Important Information for Doctors**: Highlight key points that doctors should be aware of when treating patients with this disease.
        10. **Important Information for Pharmacists**: Include details on medication interactions, side effects, and any specific instructions for pharmacists.
        11. **Important Information for Patients**: Offer guidance and reassurance for patients, emphasizing what they need to know and do to manage their condition effectively.

        Ensure that the explanation is clear, concise, and accessible to both medical professionals and patients.
        """

        try:
            response = model.generate_content(prompt)
            markdown_text = getattr(response, 'text', None)
            if markdown_text:
                html_content = markdown2.markdown(markdown_text)
                return html_content
        except Exception as e:
            print(f"Error occurred while fetching disease information: {e}")

        return "An error occurred while fetching disease information."
