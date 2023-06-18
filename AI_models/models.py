from django.db import models

# Create your models here.
class PersonalityDetectionModel(models.Model):
    personalities = models.CharField(max_length=255, default="N/A")

    def __str__(self):
        return f"Output {self.personalities}"
    
class SentimentModel(models.Model):
    value = models.CharField(max_length=255, default=0)

    def __str__(self):
        return f"Sentiment score {self.value}"

class MentalHealthDetectionModel(models.Model):
    mental_illness = models.CharField(max_length=255, default="N/A")

    def __str__(self):
        return f"Output {self.mental_illness}"