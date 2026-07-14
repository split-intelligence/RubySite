
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


from users.models import StudentProfile
from .models import Course, Category, EnrolledStudent, PaymentRecord

# Create your views here.

# ---------- Course Views ----------
def courses(request):
    courses = Course.objects.all()
    return render(request, 'courses-v1.html', {'courses': courses})


# --------- Course Detail View ----------
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'courses-details-v1.html', {'course': course})


# --------- Enroll in Course View ----------
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.is_authenticated and request.user.is_student:
        EnrolledStudent.objects.get_or_create(student=request.user.student_profile, course=course)
        return redirect('course_detail', course_id=course.id)
    else:
        return redirect('login')


# --------- Student Dashboard View ----------
@login_required
def student_dashboard(request):
    student = request.user.student_profile
    enrolled_courses = EnrolledStudent.objects.filter(student=request.user.student_profile)
    payment_status = {}
    for enrollment in enrolled_courses:
        paid = PaymentRecord.objects.filter(student=student, course=enrollment.course).exists()
        payment_status[enrollment.course.id] = paid

    return render(request, 'student-dashboard.html', {'enrolled_courses': enrolled_courses, 'payment_status': payment_status})



# ---------- Paystack Payment Initiation ----------
@login_required
def initiate_payment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.user.is_authenticated and request.user.is_student:
        student = request.user.student_profile
        
        # Check if the student is enrolled in the course
        if not EnrolledStudent.objects.filter(student=student, course=course).exists():
            return redirect('course_detail', course_id=course.id)
        
        # Check if the student has already made a payment for the course
        if PaymentRecord.objects.filter(student=student, course=course).exists():
            return redirect('student_dashboard')
        
        # Prepare Paystack data
        amount = int(course.price * 100)  # Paystack uses kobo (cents)
        email = request.user.email
        callback_url = settings.PAYSTACK_CALLBACK_URL

        payload = {
            'amount': amount,
            'email': email,
            'callback_url': callback_url,
            'metadata': {
                'student_id': student.id,
                'course_id': course.id,
            }
        }

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                'https://api.paystack.co/transaction/initialize',
                json=payload,
                headers=headers
            )
            response_data = response.json()
            if response_data['status']:
                # Redirect user to Paystack payment page
                payment_url = response_data['data']['authorization_url']
                return redirect(payment_url)
            else:
                # Handle error
                return render(request, 'payment_error.html', {'error': response_data.get('message')})
        except Exception as e:
            return render(request, 'payment_error.html', {'error': str(e)})   
    else:
        return redirect('login')


# ---------- Paystack Callback (verification) ----------
@csrf_exempt   # Paystack will POST to this URL; use csrf_exempt for simplicity (or use a non-CSRF endpoint)
def payment_callback(request):
    # Paystack sends a GET request with reference and other params
    reference = request.GET.get('reference')
    if not reference:
        return JsonResponse({'status': 'error', 'message': 'No reference provided'}, status=400)

    # Verify transaction with Paystack
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }
    verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
    try:
        response = requests.get(verify_url, headers=headers)
        response_data = response.json()
        if response_data['status'] and response_data['data']['status'] == 'success':
            # Extract metadata
            metadata = response_data['data']['metadata']
            student_id = metadata.get('student_id')
            course_id = metadata.get('course_id')
            if not student_id or not course_id:
                return JsonResponse({'status': 'error', 'message': 'Missing metadata'}, status=400)

            student = get_object_or_404(StudentProfile, id=student_id)
            course = get_object_or_404(Course, id=course_id)

            # Check if payment already recorded
            if not PaymentRecord.objects.filter(student=student, course=course).exists():
                # Create payment record
                PaymentRecord.objects.create(
                    student=student,
                    course=course,
                    amount=course.price,
                    transaction_id=reference,
                    payment_method='Paystack'
                )
                # Optionally, mark enrollment as completed or update progress? Not required.

            return render(request, 'payment_success.html')
        else:
            return render(request, 'payment_error.html', {'error': 'Payment verification failed'})
    except Exception as e:
        return render(request, 'payment_error.html', {'error': str(e)})