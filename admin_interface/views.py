from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import RegisteredPerson, MatchedCase
from user.models import ReportedCase
from .utils import cnn_knn_matching

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "admin" and password == "admin":
            return redirect("admin_interface:dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "admin_interface/admin_login.html")

def register_person(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        name = request.POST.get('name')
        age = request.POST.get('age')
        date_missing = request.POST.get('date_missing')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        photo = request.FILES['photo']
        
        try:
            width, height = get_image_dimensions(photo)
            if width > 1000 or height > 1000:
                messages.error(request, "Image is too large. Please upload a smaller image.")
                return render(request, 'admin_interface/register_person.html')

        except ValidationError:
            messages.error(request, "Invalid image file.")
            return render(request, 'admin_interface/register_person.html')

        person = RegisteredPerson.objects.create(
            name=name, 
            age=age, 
            date_missing=date_missing, 
            phone=phone, 
            email=email,
            photo=photo
        )
        
        find_matches()
        return redirect('admin_interface:success')
    
    return render(request, 'admin_interface/register_person.html')

def find_matches():
    registered_cases = RegisteredPerson.objects.all()
    reported_cases = ReportedCase.objects.all()
    
    for reg in registered_cases:
        for rep in reported_cases:
            match_score = cnn_knn_matching(reg.photo.path, rep.photo.path)
            if match_score > 0.8:
                MatchedCase.objects.get_or_create(
                    registered_person=reg, 
                    reported_case=rep,
                    defaults={'match_percentage': match_score}  # Ensure 'match_percentage' is added here
                )
def matched_cases(request):
    cases = MatchedCase.objects.all()
    return render(request, 'admin_interface/matched_cases.html', {'cases': cases})

def registered_cases(request):
    cases = RegisteredPerson.objects.all()
    return render(request, 'admin_interface/registered_cases.html', {'cases': cases})

def reported_cases(request):
    cases = ReportedCase.objects.all()
    return render(request, 'admin_interface/reported_cases.html', {'cases': cases})

def dashboard(request):
    return render(request, 'admin_interface/dashboard.html')

def success(request):
    return render(request, 'admin_interface/success.html', {'message': 'Person registered successfully!'})

def view_case(request, case_id):
    case = get_object_or_404(RegisteredPerson, id=case_id)
    return render(request, 'admin_interface/view_case.html', {'case': case})

def delete_case(request, case_id, case_type):
    # Determine the model based on the case_type parameter
    if case_type == 'registered':
        case = get_object_or_404(RegisteredPerson, id=case_id)
    elif case_type == 'reported':
        case = get_object_or_404(ReportedCase, id=case_id)
    else:
        # Return a 404 error if case_type is invalid
        return redirect('admin_interface:reported_cases')
    
    if request.method == 'POST':  # Ensure POST method is used for deletion
        case.delete()  # Delete the case from the database
        if case_type == 'registered':
            return redirect('admin_interface:registered_cases')
        elif case_type == 'reported':
            return redirect('admin_interface:reported_cases')
    
    # If not POST, render a confirmation page (optional for each case type)
    return render(request, 'admin_interface/confirm_delete.html', {'case': case})

def confirm_delete(request, id):
    case = get_object_or_404(RegisteredPerson, id=id)
    return render(request, 'admin_interface/confirm_delete.html', {'case': case})
