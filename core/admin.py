from django.contrib import admin
from .models import Symptom, DiseaseSymptom, Disease, Prediction, Hospital

# Register your models here.

admin.site.register(Symptom)
admin.site.register(Disease)
admin.site.register(Hospital)

