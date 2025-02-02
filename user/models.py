from django.db import models

class ReportedCase(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    # details = models.TextField()
    photo = models.ImageField(upload_to='reported_images/')
    reported_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, default='No description')


    def __str__(self):
        return self.name