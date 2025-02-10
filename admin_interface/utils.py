import os
import cv2
import insightface
import numpy as np
from scipy.spatial.distance import cosine
from django.core.files.storage import default_storage
from .models import RegisteredPerson, MatchedCase ,AgeProgressedImage # Import your models
from user.models import ReportedCase
import logging
from django.conf import settings

# Set up logging for debugging
logger = logging.getLogger(__name__)

# Load ArcFace Model
model = insightface.app.FaceAnalysis(name="buffalo_l")
model.prepare(ctx_id=-1)  # Run on CPU
from django.core.mail import send_mail
from django.conf import settings

def send_match_notification(matched_case):
    """Send an email to the registered person when a match is found."""
    subject = "🔔 Match Found: Possible Identification"
    message = f"""
    Dear {matched_case.registered_person.name},

    We have found a potential match for {matched_case.registered_person.name}.
    Matched with: {matched_case.reported_case.name}
    
    Please check your dashboard or contact authorities for further verification.

    Regards,
    Your Team
    """
    
    recipient_email = matched_case.registered_person.email  # Assuming the model has an email field

    if recipient_email:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender email
            [recipient_email],  # Recipient email
            fail_silently=False,
        )
        print(f"📧 Email sent to {recipient_email}")
    else:
        print("❌ No email found for the registered person.")



def preprocess_image(image_path):
    """Resize the image before passing to the face model"""
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found - {image_path}")
        return None

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Unable to read image - {image_path}")
        return None

    img = cv2.resize(img, (112, 112))  # Resize to fit model requirements
    return img

def get_face_embedding(image_path):
    """Extract 512-D face embedding using ArcFace"""
    img = preprocess_image(image_path)
    if img is None:
        return None

    faces = model.get(img)
    if len(faces) == 0:
        print(f"❌ No face detected in {image_path}")  
        return None  # No face detected
    
    print(f"✅ Face detected in: {image_path}")
    return faces[0].embedding  # 512-D vector

def compare_faces(image1, image2, threshold=0.6):
    """Compare two face embeddings using cosine similarity"""
    emb1 = get_face_embedding(image1)
    emb2 = get_face_embedding(image2)

    if emb1 is None or emb2 is None:
        print(f"❌ Face detection failed for one or both images: {image1}, {image2}")
        return False  # No face detected

    distance = cosine(emb1, emb2)  # Compute similarity
    print(f"📏 Cosine distance: {distance} between {image1} and {image2}")
    return distance < threshold  # Returns True if match
# use if age progression not needed 
# def check_match_on_register(registered_case):
#     """When a missing person is registered, check with all reported cases"""
#     registered_image = os.path.join(settings.MEDIA_ROOT, str(registered_case.photo))
#     print(f"🔍 Checking registered person image: {registered_image}")

#     # Fetch reported cases
#     reported_cases = ReportedCase.objects.all()
#     print(f"Total reported cases: {reported_cases.count()}") 
#     if not reported_cases.exists():
#         print("❌ No reported cases found in the database.")
#         return

#     print(f"✅ {reported_cases.count()} reported cases found. Processing...")

#     for reported_case in reported_cases:
#         reported_image = os.path.join(settings.MEDIA_ROOT, str(reported_case.photo))
#         print(f"🆚 Comparing with reported case image: {reported_image}")
#         print(f"Type of reported_case: {type(reported_case)}")

#         if compare_faces(registered_image, reported_image):
#             # Store the match in the database
#             match = MatchedCase.objects.create(
#     registered_person=registered_case,
#     reported_case=reported_case,  # Ensure you're fetching a valid instance
#     match_percentage=1.0  # Placeholder for match percentage
# )

#             print(f"✅ Match found! {registered_case.name} ↔ {reported_case.name}")
# utils.py or wherever your matching logic is defined


def check_match_on_register(registered_case):
    # Path for the registered case image
    registered_image = os.path.join(settings.MEDIA_ROOT, str(registered_case.photo))
    
    # Fetch all age-progressed images of this person
    age_progressed_images = AgeProgressedImage.objects.filter(registered_person=registered_case)

    # Get all reported cases
    reported_cases = ReportedCase.objects.all()

    # If no reported cases, skip matching process
    if not reported_cases.exists():
        return

    # Loop through each reported case to compare
    for reported_case in reported_cases:
        reported_image = os.path.join(settings.MEDIA_ROOT, str(reported_case.photo))

        # Compare original image
        if compare_faces(registered_image, reported_image):
            # Check if the match already exists to avoid duplicates
            if not MatchedCase.objects.filter(registered_person=registered_case, reported_case=reported_case).exists():
                match=MatchedCase.objects.create(
                    registered_person=registered_case,
                    reported_case=reported_case,
                    match_percentage=100 # Perfect match for original image
                )
                send_match_notification(match)
                


        # Loop through each age-progressed image and compare
        for progressed in age_progressed_images:
            progressed_image_path = os.path.join(settings.MEDIA_ROOT, str(progressed.photo))
            if compare_faces(progressed_image_path, reported_image):
                # Check if the match already exists to avoid duplicates
                if not MatchedCase.objects.filter(registered_person=registered_case, reported_case=reported_case).exists():
                    MatchedCase.objects.create(
                        registered_person=registered_case,
                        reported_case=reported_case,
                        match_percentage=0.8  # Lower confidence for age-progressed images
                    )
        

def check_match_on_report(reported_case):
    """When a suspected person is reported, check with all registered cases"""
    reported_image = os.path.join("media", str(reported_case.photo))
    print(f"🔍 Checking reported case image: {reported_image}")

    # Fetch registered cases
    registered_cases = RegisteredPerson.objects.all()
    if not registered_cases.exists():
        print("❌ No registered persons found in the database.")
        return

    print(f"✅ {registered_cases.count()} registered persons found. Processing...")

    for registered_case in registered_cases:
        registered_image = os.path.join("media", str(registered_case.photo))
        print(f"🆚 Comparing with registered case image: {registered_image}")

        if compare_faces(registered_image, reported_image):
            # Store the match in the database
            match = MatchedCase.objects.create(
                registered_person=registered_case,
                reported_case=reported_case,
                match_percentage=100 # Placeholder for match percentage
            )
            print(f"✅ Match found! {registered_case.name} ↔ {reported_case.name}")
            send_match_notification(match)
