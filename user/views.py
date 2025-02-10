from django.shortcuts import render, redirect
from .models import ReportedCase
from django.shortcuts import render, redirect
from django.contrib import messages  # Fix: Import messages
from django.core.exceptions import ValidationError  # Fix: Import ValidationError
from django.core.files.images import get_image_dimensions  # Fix: Import get_image_dimensions
from .models import ReportedCase
from admin_interface.models import RegisteredPerson  # Ensure you import your models
from admin_interface.utils import check_match_on_report  # Fix: Import check_match_on_report function


def home(request):
    return render(request, 'user/home.html')

def user_login(request):
    return render(request, 'user/user_login.html')

def report_missing_person(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        name = request.POST.get('name')
        location = request.POST.get('location')
        photo = request.FILES['photo']

        if not all([name, location, photo]):  # Ensure all fields are provided
            messages.error(request, "All fields are required!")
            return render(request, 'user/report_person.html')

        try:
            width, height = get_image_dimensions(photo)
            if width > 1000 or height > 1000:
                messages.error(request, "Image is too large. Please upload a smaller image.")
                return render(request, 'user/report_person.html')

        except ValidationError:
            messages.error(request, "Invalid image file.")
            return render(request, 'user/report_person.html')

        reported_case = ReportedCase.objects.create(
            name=name,
            location=location,
            photo=photo
        )

        # After reporting a missing person, check for matches in registered persons
        check_match_on_report(reported_case)

        return redirect('admin_interface:success')  # Update this with the correct success URL

    return render(request, 'user/report_person.html')
