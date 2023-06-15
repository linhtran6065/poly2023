from django.db import models

# Create your models here.
class PersonalityDetectionModel(models.Model):
    personalities = models.CharField(max_length=255, default="N/A")

    def __str__(self):
        return f"Output {self.personalities}"