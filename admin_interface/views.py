import os
import base64
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from .models import RegisteredPerson, MatchedCase,AgeProgressedImage 
from user.models import ReportedCase
from .utils import check_match_on_register, check_match_on_report
from django.http import JsonResponse
from PIL import Image
from io import BytesIO

# Use the correct Flask API URL
FLASK_API_URL = "http://3bfd-34-124-146-94.ngrok-free.app/"  # Update with your ngrok URL


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username == "admin" and password == "admin":
            return redirect("admin_interface:dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "admin_interface/admin_login.html")

#without age progression use this 
# def register_person(request):
#     if request.method == 'POST' and request.FILES.get('photo'):
#         name = request.POST.get('name')
#         age = request.POST.get('age')
#         date_missing = request.POST.get('date_missing')
#         phone = request.POST.get('phone')
#         email = request.POST.get('email')
#         photo = request.FILES['photo']
        
#         try:
#             width, height = get_image_dimensions(photo)
#             if width > 1000 or height > 1000:
#                 messages.error(request, "Image is too large. Please upload a smaller image.")
#                 return render(request, 'admin_interface/register_person.html')

#         except ValidationError:
#             messages.error(request, "Invalid image file.")
#             return render(request, 'admin_interface/register_person.html')

#         person = RegisteredPerson.objects.create(
#             name=name, 
#             age=age, 
#             date_missing=date_missing, 
#             phone=phone, 
#             email=email,
#             photo=photo
#         )
        
#         # After registering a person, check for any potential matches in reported cases
#         check_match_on_register(person)
#         return redirect('admin_interface:success')
    
#     return render(request, 'admin_interface/register_person.html')

#for age progressed integration use this 
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image

def register_person(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        name = request.POST.get('name')
        age = int(request.POST.get('age'))
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

        # Generate age-progressed images
        age_gaps = [10, 20, 30, 40, 50]  # Example: generate for 10, 20, 30, 40, 50 years
        age_progressed_images = []

        for target_age in age_gaps:
            progressed_image = generate_age_progressed(photo, target_age)
            if progressed_image:
                age_progressed_images.append(progressed_image)

        # Store age-progressed images in the database
        for img in age_progressed_images:
            # Convert the image to InMemoryUploadedFile
            image = Image.open(img["image_file"])
            img_io = BytesIO()
            image.save(img_io, format="JPEG")
            img_io.seek(0)
            in_memory_file = InMemoryUploadedFile(
                img_io, None, f"{img['age_target']}_age_progressed.jpg", 'image/jpeg', img_io.tell(), None
            )

            # Create the AgeProgressedImage object with the InMemoryUploadedFile
            AgeProgressedImage.objects.create(
                registered_person=person,
                age_target=img["age_target"],
                photo=in_memory_file
            )

        # Check for potential matches in reported cases
        check_match_on_register(person)

        return redirect('admin_interface:success')

    return render(request, 'admin_interface/register_person.html')


def matched_cases(request):
    cases = MatchedCase.objects.all()
    return render(request, 'admin_interface/matched_cases.html', {'cases': cases})


def registered_cases(request):
    cases = RegisteredPerson.objects.all()
    return render(request, 'admin_interface/registered_cases.html', {'cases': cases})


def reported_cases(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        name = request.POST.get('name')
        location = request.POST.get('location')
        photo = request.FILES['photo']
        
        reported_case = ReportedCase.objects.create(
            name=name,
            location=location,
            photo=photo
        )
        
        # After reporting a case, check for any potential matches in registered cases
        check_match_on_report(reported_case)
        return redirect('admin_interface:success')
    
    cases = ReportedCase.objects.all()
    return render(request, 'admin_interface/reported_cases.html', {'cases': cases})


def dashboard(request):
    return render(request, 'admin_interface/dashboard.html')


def success(request):
    return render(request, 'admin_interface/success.html', {'message': 'Operation completed successfully!'})


def view_case(request, case_id):
    case = get_object_or_404(RegisteredPerson, id=case_id)
    return render(request, 'admin_interface/view_case.html', {'case': case})


def delete_case(request, case_id, case_type):
    if case_type == 'registered':
        case = get_object_or_404(RegisteredPerson, id=case_id)
    elif case_type == 'reported':
        case = get_object_or_404(ReportedCase, id=case_id)
    else:
        return redirect('admin_interface:reported_cases')
    
    if request.method == 'POST':
        case.delete()
        if case_type == 'registered':
            return redirect('admin_interface:registered_cases')
        elif case_type == 'reported':
            return redirect('admin_interface:reported_cases')
    
    return render(request, 'admin_interface/confirm_delete.html', {'case': case})


def age_progress_view(request):
    if request.method == "POST":
        try:
            # Get the uploaded image and target age from the request
            image_file = request.FILES['photo']
            target_age = int(request.POST['age_target'])

            # Convert image to base64
            image = Image.open(image_file).convert("RGB")
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Prepare the data to send to the Flask API
            data = {
                "image": image_base64,
                "age_target": target_age
            }

            # Log the data to help debug
            print(f"Sending data to Flask API: {data}")

            # Send the request to the Flask API
            response = requests.post(f"{FLASK_API_URL}/age-progress", json=data)

            if response.status_code == 200:
                # Extract the base64 image from the response
                result = response.json()
                processed_image_base64 = result.get("processed_image")

                # Return the processed image in base64
                return JsonResponse({"processed_image": processed_image_base64})

            else:
                # Log the error message from Flask API
                print(f"Error from Flask API: {response.text}")
                return JsonResponse({"error": "Failed to process the image"}, status=500)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, 'admin_interface/age_progress.html')
#for age progressed image remove if age progression is not needed 
def generate_age_progressed(image_file, target_age):
    """Send an image to the Flask API for age progression"""
    try:
        # Convert image to base64
        image = Image.open(image_file).convert("RGB")
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Prepare data for API request
        data = {
            "image": image_base64,
            "age_target": target_age
        }

        response = requests.post(f"{FLASK_API_URL}/age-progress", json=data)

        if response.status_code == 200:
            result = response.json()
            processed_image_base64 = result.get("processed_image")

            # Convert base64 to Django file
            processed_image = base64.b64decode(processed_image_base64)
            image_file = BytesIO(processed_image)

            return {"age_target": target_age, "image_file": image_file}

        else:
            print(f"Error from Flask API: {response.text}")
            return None

    except Exception as e:
        print(f"Error generating age-progressed image: {e}")
        return None
def view_age_progressed(request, registered_person_id):
    registered_person = get_object_or_404(RegisteredPerson, id=registered_person_id)
    age_progressed_images = AgeProgressedImage.objects.filter(registered_person=registered_person)

    return render(request, 'admin_interface/view_age_progressed.html', {'person': registered_person, 'images': age_progressed_images})