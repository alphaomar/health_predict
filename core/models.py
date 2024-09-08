from django.db import models


class Symptom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Disease(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    symptoms = models.ManyToManyField(Symptom, through='DiseaseSymptom')

    def __str__(self):
        return self.name


class DiseaseSymptom(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    relevance = models.IntegerField(default=0)  # e.g., relevance score from 0 to 100

    def __str__(self):
        return f"{self.disease.name} - {self.symptom.name}"


class Prediction(models.Model):
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    symptoms = models.ManyToManyField(Symptom)
    probability = models.FloatField()  # Probability score for the prediction
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Disease: {self.disease.name}, Probability: {self.probability:.2f}"


class Hospital(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    local_address_desc = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    hospital_image = models.ImageField(upload_to='hospitals/', null=True, blank=True)
    region = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
