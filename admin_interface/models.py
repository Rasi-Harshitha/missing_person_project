from django.db import models

class RegisteredPerson(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    date_missing = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    photo = models.ImageField(upload_to='registered_photos/')
    address = models.TextField()

    def __str__(self):
        return self.name


class ReportedCase(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    # details = models.TextField()
    photo = models.ImageField(upload_to='reported_images/')
    reported_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, default='No description')


    def __str__(self):
        return self.name


class MatchedCase(models.Model):
    registered_person = models.ForeignKey(RegisteredPerson, on_delete=models.CASCADE)
    reported_case = models.ForeignKey(ReportedCase, on_delete=models.CASCADE)
    match_percentage = models.FloatField()  # ADD THIS FIELD
    match_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registered_person.name} matched with {self.reported_case.name} ({self.match_percentage * 100:.2f}%)"
    