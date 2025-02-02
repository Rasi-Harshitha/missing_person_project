from django.shortcuts import render, redirect
from .models import ReportedCase

def home(request):
    return render(request, 'user/home.html')

def user_login(request):
    return render(request, 'user/user_login.html')

def report_missing_person(request):
    if request.method == 'POST':
        location = request.POST['location']
        photo = request.FILES['photo']  # Ensure the form uses 'photo' as the name

        # Use 'photo' instead of 'image' to match the model field
        ReportedCase.objects.create(location=location, photo=photo)  
        return redirect('/')  # Redirect to the homepage or a success page

    return render(request, 'user/report_person.html')