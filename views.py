from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import EmailMessage
import json
import os

@require_http_methods(["GET"])
def form_view(request):
    """Display the student details form"""
    return render(request, 'form.html')

@csrf_exempt
@require_http_methods(["POST"])
def submit_form(request):
    """Handle form submission"""
    try:
        # Get form data
        name = request.POST.get('name', '')
        rollnumber = request.POST.get('rollnumber', '')
        payment = request.POST.get('payment', '')
        photo = request.FILES.get('photo', None)
        
        # Validate
        if not all([name, rollnumber, payment]):
            return JsonResponse({
                'success': False,
                'message': 'Please fill all required fields'
            }, status=400)
        
        if not photo:
            return JsonResponse({
                'success': False,
                'message': 'Please upload a photo'
            }, status=400)
        
        # Save photo
        os.makedirs('media', exist_ok=True)
        photo_name = f"photo_{rollnumber}_{photo.name}"
        photo_path = os.path.join('media', photo_name)
        
        with open(photo_path, 'wb+') as destination:
            for chunk in photo.chunks():
                destination.write(chunk)
        
        # Save submission data
        submission = {
            'name': name,
            'rollnumber': rollnumber,
            'payment': payment,
            'photo': photo_name
        }
        
        # Save to JSON file (you can extend this to save to database)
        submissions_file = 'submissions.json'
        submissions = []
        
        if os.path.exists(submissions_file):
            with open(submissions_file, 'r') as f:
                submissions = json.load(f)
        
        submissions.append(submission)
        
        with open(submissions_file, 'w') as f:
            json.dump(submissions, f, indent=4)
        
        # Send Email
        try:
            subject = f'New Form Submission: {name} ({rollnumber})'
            body = f"""
            New student details submitted:
            
            Name: {name}
            Roll Number: {rollnumber}
            Payment Method: {payment}
            
            Please see the attached photo.
            """
            
            email = EmailMessage(
                subject,
                body,
                settings.EMAIL_FROM,
                ['lllllathavadla@gmail.com'],
            )
            
            # Attach the photo
            with open(photo_path, 'rb') as f:
                email.attach(photo_name, f.read(), photo.content_type)
            
            email.send()
            email_sent = True
        except Exception as email_err:
            print(f"Email sending failed: {str(email_err)}")
            email_sent = False
        
        return JsonResponse({
            'success': True,
            'message': 'Form submitted successfully!' + (' Email sent.' if email_sent else ' However, email notification failed.'),
            'data': submission
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
