from django.contrib import admin
from .models import RegisteredPerson, ReportedCase, MatchedCase

admin.site.register(RegisteredPerson)
admin.site.register(ReportedCase)
admin.site.register(MatchedCase)
# Register your models here.
