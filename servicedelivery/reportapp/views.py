from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from .models import Complaint, ComplaintUpdate, Rating
from mainapp.models import ChatMessage


def lodge_complaint(request):
    """View for lodging a new complaint."""
    if request.method == 'POST':
        is_anonymous = request.POST.get('is_anonymous') == 'on'

        # Build complaint object
        complaint = Complaint(
            is_anonymous=is_anonymous,
            category=request.POST.get('category', 'other'),
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
            location_address=request.POST.get('location_address', ''),
            ward_number=request.POST.get('ward_number', ''),
            notify_whatsapp=request.POST.get('notify_whatsapp') == 'on',
            notify_email=request.POST.get('notify_email') == 'on',
            notify_sms=request.POST.get('notify_sms') == 'on',
        )

        if request.user.is_authenticated:
            complaint.user = request.user
            complaint.first_name = request.user.first_name
            complaint.last_name = request.user.last_name
            complaint.email = request.user.email

        if not is_anonymous:
            complaint.first_name = request.POST.get('first_name', complaint.first_name)
            complaint.last_name = request.POST.get('last_name', complaint.last_name)
            complaint.email = request.POST.get('email', complaint.email)
            complaint.phone = request.POST.get('phone', '')

        # Handle photo upload
        if 'photo' in request.FILES:
            complaint.photo = request.FILES['photo']

        complaint.status = 'submitted'
        complaint.save()

        # Create initial update entry
        ComplaintUpdate.objects.create(
            complaint=complaint,
            message='Your complaint has been received and is now in our system. A team member will review it shortly.',
            updated_by='System',
            new_status='submitted'
        )

        # Store reference number in session for confirmation
        request.session['last_reference'] = complaint.reference_number
        request.session['last_complaint_id'] = complaint.id

        messages.success(
            request,
            f'Your complaint has been successfully submitted! Your reference number is {complaint.reference_number}. '
            f'Please save this number to track your complaint status.'
        )
        return redirect('complaint_success', ref=complaint.reference_number)

    # GET: show the form
    categories = Complaint.CATEGORY_CHOICES
    context = {
        'categories': categories,
    }
    return render(request, 'reportapp/lodge_complaint.html', context)


def complaint_success(request, ref):
    """Success page shown after complaint submission."""
    complaint = get_object_or_404(Complaint, reference_number=ref)
    return render(request, 'reportapp/complaint_success.html', {'complaint': complaint})


def track_complaint(request):
    """View for tracking complaint status."""
    complaint = None
    error = None

    if request.method == 'POST':
        ref = request.POST.get('reference_number', '').strip().upper()
        try:
            complaint = Complaint.objects.get(reference_number=ref)
        except Complaint.DoesNotExist:
            error = f'No complaint found with reference number "{ref}". Please check and try again.'

    context = {
        'complaint': complaint,
        'error': error,
    }
    return render(request, 'reportapp/track_complaint.html', context)


def submit_rating(request):
    """Submit a rating for a resolved complaint."""
    if request.method == 'POST':
        ref = request.POST.get('reference_number', '').strip().upper()
        stars = request.POST.get('stars', 0)
        comment = request.POST.get('comment', '')

        try:
            complaint = Complaint.objects.get(reference_number=ref)
            rating, created = Rating.objects.get_or_create(
                complaint=complaint,
                defaults={'stars': int(stars), 'comment': comment}
            )
            if not created:
                rating.stars = int(stars)
                rating.comment = comment
                rating.save()

            messages.success(request, 'Thank you for your feedback! Your rating has been recorded.')
            return redirect('track_complaint')
        except Complaint.DoesNotExist:
            messages.error(request, 'Complaint not found.')
            return redirect('track_complaint')

    return redirect('track_complaint')


def report_chat_api(request):
    """Chat API for the report/track pages."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg_text = data.get('message', '').strip()
            page = data.get('page', 'report')

            if not msg_text:
                return JsonResponse({'error': 'Empty message'}, status=400)

            name = 'Anonymous'
            if request.user.is_authenticated:
                name = request.user.get_full_name() or request.user.username

            ChatMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                message=msg_text,
                page=page
            )

            msg_lower = msg_text.lower()
            if any(w in msg_lower for w in ['hello', 'hi', 'hey']):
                reply = "Hello! I am here to assist you with your service delivery complaint. How can I help?"
            elif any(w in msg_lower for w in ['how long', 'when', 'time', 'days']):
                reply = "Resolution times vary by category. Water and electricity issues are prioritised within 48 hours. Roads and general complaints may take 7-14 working days. Urgent safety hazards are attended to within 4 hours."
            elif any(w in msg_lower for w in ['whatsapp', 'phone', 'call', 'contact']):
                reply = "WhatsApp: +27 10 123 4567 | Helpline: 0800 601 709 (toll-free) | Office hours: Mon-Fri 07:00-17:00. After hours emergency line available for urgent hazards."
            elif any(w in msg_lower for w in ['reference', 'number', 'track']):
                reply = "Your reference number was emailed to you after submission. Use it on the 'Track My Complaint' page to monitor progress in real time."
            elif any(w in msg_lower for w in ['photo', 'picture', 'image', 'upload']):
                reply = "Yes, you may attach a photograph when lodging your complaint. This helps our field teams locate and assess the issue faster."
            elif any(w in msg_lower for w in ['status', 'update', 'progress']):
                reply = "You can track your complaint status using your reference number on the tracking page. Status moves through: Pending, Submitted, In Progress, Resolved, and Closed."
            elif any(w in msg_lower for w in ['cancel', 'withdraw', 'delete']):
                reply = "To withdraw a complaint, please call our helpline at 0800 601 709 with your reference number ready."
            else:
                reply = "Thank you for your message. A support agent will follow up within 2 business hours. For urgent matters, call 0800 601 709."

            ChatMessage.objects.create(
                name='Support Agent',
                message=reply,
                is_staff_reply=True,
                page=page
            )

            recent = ChatMessage.objects.filter(page=page).order_by('-timestamp')[:30]
            chat_data = [
                {
                    'name': m.name,
                    'message': m.message,
                    'is_staff': m.is_staff_reply,
                    'time': m.timestamp.strftime('%H:%M')
                }
                for m in reversed(list(recent))
            ]
            return JsonResponse({'messages': chat_data})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'GET':
        page = request.GET.get('page', 'report')
        recent = ChatMessage.objects.filter(page=page).order_by('-timestamp')[:30]
        chat_data = [
            {
                'name': m.name,
                'message': m.message,
                'is_staff': m.is_staff_reply,
                'time': m.timestamp.strftime('%H:%M')
            }
            for m in reversed(list(recent))
        ]
        return JsonResponse({'messages': chat_data})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
