from django.db import models

# Create your models here.
class Detection(models.Model):
    image_url = models.URLField()  # Appwrite image URL
    gemini_response = models.TextField()  # Stored in Firebase, but reference here if needed
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detection at {self.timestamp}"