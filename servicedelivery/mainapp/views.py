from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChatMessage


def home(request):
    """Main landing page - handles login, signup, and anonymous access."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')

        elif action == 'signup':
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken. Please choose another.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome, {first_name or username}!')
                return redirect('home')

        elif action == 'anonymous':
            request.session['is_anonymous'] = True
            messages.info(request, 'You are browsing anonymously. You can still lodge a complaint.')
            return redirect('home')

    return render(request, 'mainapp/home.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def chat_api(request):
    """API endpoint for chat messages."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            msg_text = data.get('message', '').strip()
            page = data.get('page', 'home')

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

            # Auto-reply logic
            msg_lower = msg_text.lower()
            if any(w in msg_lower for w in ['hello', 'hi', 'hey', 'good']):
                reply = "Hello! Welcome to the Service Delivery Portal. How can we assist you today?"
            elif any(w in msg_lower for w in ['report', 'complain', 'complaint', 'problem', 'issue']):
                reply = "To lodge a complaint, click the 'Lodge a Complaint' button in the navigation bar or on the homepage. You will receive a reference number once submitted."
            elif any(w in msg_lower for w in ['track', 'status', 'reference', 'update']):
                reply = "You can track your complaint using the 'Track My Complaint' button on the homepage. Enter your reference number to see real-time status updates."
            elif any(w in msg_lower for w in ['whatsapp', 'phone', 'call', 'contact']):
                reply = "You can contact us via WhatsApp at +27 10 123 4567 or call our helpline at 0800 601 709 (toll-free). We are available Monday to Friday, 07:00 - 17:00."
            elif any(w in msg_lower for w in ['language', 'zulu', 'xhosa', 'afrikaans', 'sotho']):
                reply = "We currently support English, Zulu, Xhosa, Afrikaans, and Sotho. Use the Help menu in the top navigation to change your preferred language."
            elif any(w in msg_lower for w in ['anonymous', 'private', 'name']):
                reply = "Yes, you may submit a complaint anonymously. Simply select 'Continue Anonymously' on the login form and your identity will remain protected."
            elif any(w in msg_lower for w in ['urgent', 'emergency', 'dangerous', 'hazard']):
                reply = "For urgent safety hazards such as exposed electricity or burst water pipes, please call our emergency line: 0800 601 709 immediately. We respond within 4 hours."
            else:
                reply = "Thank you for your message. A support agent will respond shortly. For immediate assistance, call 0800 601 709 or WhatsApp +27 10 123 4567."

            ChatMessage.objects.create(
                name='Support Team',
                message=reply,
                is_staff_reply=True,
                page=page
            )

            recent = ChatMessage.objects.filter(page=page).order_by('-timestamp')[:20]
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
        page = request.GET.get('page', 'home')
        recent = ChatMessage.objects.filter(page=page).order_by('-timestamp')[:20]
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
