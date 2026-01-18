from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Service, Reservation, BlogPost
from twilio.rest import Client
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from .models import Review
import datetime
import json


def services_list(request):
    services = Service.objects.all()
    return render(request, 'main/services_list.html', {'services': services})


def index(request):
    services = Service.objects.all()
    return render(request, 'main/index.html', {'services': services})


def calendar(request):
    services = Service.objects.all()
    # List of days (e.g., Monday–Sunday)
    start_date = datetime.date.today()
    week_days = [(start_date + datetime.timedelta(days=i)) for i in range(7)]
    reservations = Reservation.objects.select_related(
        "service"
    ).filter(date__in=week_days)
    reserved_slots = [
        {
            "date": r.date,
            "time": r.time.strftime("%H:%M"),
            "service": r.service.title,
            "service_duration": r.service.time,
        }
        for r in reservations
    ]
    # List of hours, e.g., from 8:00 to 18:00 in 1-hour intervals
    hours = [f"{h:02d}:00" for h in range(8, 19)]
    return render(
        request, 'main/calendar.html',
        {
            'services': services,
            'week_days': week_days,
            'hours': hours,
            'reserved_slots': reserved_slots
        }
    )


def calendar_view(request):
    start_date = datetime.date.today()
    week_days = [(start_date + datetime.timedelta(days=i)) for i in range(7)]
    hours = [f"{h:02d}:00" for h in range(8, 20)]

    # Reservations
    reservations = Reservation.objects.select_related(
        "service"
    ).filter(date__in=week_days)
    reserved_map = {}  # (hour, date) -> (title, duration)
    for r in reservations:
        start_hour = r.time.hour
        duration = r.service.time  # Number of hours
        for i in range(duration):
            hour = f"{start_hour + i:02d}:00"
            reserved_map[(hour, r.date)] = (
                r.service.title,
                duration,
                r.user,
                r.id
            )
    print(reserved_map)

    # Building a table: list of rows
    table = []
    for h in hours:
        row = []
        for d in week_days:
            service = reserved_map.get((h, d))
            if service:
                row.append({
                    "hour": h,
                    "date": d,
                    "reserved": bool(service),
                    "service": service[0],
                    "user": service[2],
                    "id": service[3]
                })
            else:
                row.append({
                    "hour": h,
                    "date": d,
                    "reserved": bool(service),
                    "service": "Zarezerwuj",
                    "user": 0,
                    "id": 0,
                })

        table.append({"hour": h, "slots": row})

    return render(request, 'main/calendar.html', {
        "week_days": week_days,
        "table": table
    })


def twillo_send(message):
    try:
        # Data from Twilio dashboard
        with open("config.json") as f:
            config = json.load(f)

            account_sid = config["ACCOUNT_SID"]
            auth_token = config["AUTH_TOKEN"]
            twilio_number = config["TWILIO_NUMBER"]
            to_number = config["TO_NUMBER"]
            client = Client(account_sid, auth_token)
            sms = client.messages.create(
                body=message,
                from_=twilio_number,
                to=to_number
            )
            print(f"SMS sent! SID: {sms.sid}")
    except Exception as e:
        print("Error:", e)


@login_required(login_url='login')
def reservation(request):
    services = Service.objects.all()
    selected_date = request.GET.get("date")  # e.g., '2025-09-17'
    selected_hour = request.GET.get("hour")  # e.g., '10:00'
    # Reservations
    start_date = datetime.date.today()
    week_days = [(start_date + datetime.timedelta(days=i)) for i in range(7)]
    hours = [f"{h:02d}:00" for h in range(8, 20)]
    reservations = Reservation.objects.select_related(
        "service"
    ).filter(date__in=week_days)
    reserved_map = {}  # (hour, date) -> (title, duration)
    for r in reservations:
        start_hour = r.time.hour
        duration = r.service.time  # Number of hours
        for i in range(duration):
            hour = f"{start_hour + i:02d}:00"
            reserved_map[(hour, r.date)] = (r.service.title, duration)
    print(reserved_map)
    hours = [f"{h:02d}:00" for h in range(8, 19)]
    # Filter out the occupied hours for the selected day
    if selected_date:
        try:
            selected_date_obj = datetime.datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()
            hours = [
                hour for hour in hours
                if (hour, selected_date_obj) not in reserved_map
            ]
        except ValueError:
            pass

    if request.method == "POST":
        service_id = request.POST.get("service")
        date = request.POST.get("date")
        time = request.POST.get("hour")
        time_obj = datetime.datetime.strptime(time, "%H:%M").time()

        service = Service.objects.get(id=service_id)
        Reservation.objects.create(
                user=request.user,
                service=service,
                date=date,
                time=time_obj
            )
        twillo_send("New Reservation " + str(date))
        return redirect("calendar")
    return render(
        request,
        'main/reservation.html',
        {
            'services': services,
            'hours': hours,
            "selected_date": selected_date,
            "selected_hour": selected_hour,
        }
    )


@login_required(login_url='login')
def manage_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    services = Service.objects.all()
    hours = [f"{h:02d}:00" for h in range(8, 20)]

    if request.method == "POST":
        # If delete was clicked
        if "delete" in request.POST:
            reservation.delete()
            return redirect("calendar")

        # Editing an existing reservation
        service_id = request.POST.get("service")
        date = request.POST.get("date")
        time = request.POST.get("hour")

        service = get_object_or_404(Service, pk=service_id)
        time_obj = datetime.datetime.strptime(time, "%H:%M").time()

        # Modification of an existing object
        reservation.service = service
        reservation.date = date
        reservation.time = time_obj
        reservation.save()

        return redirect("calendar")

    return render(request, "main/manage_reservation.html", {
        "reservation": reservation,
        "services": services,
        "hours": hours,
    })


def resume(request):
    services = Service.objects.all()
    return render(request, 'main/about_me.html', {'services': services})


def services(request):
    services = Service.objects.all()
    return render(request, 'main/services.html', {'services': services})


def user_login(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # We differentiate between forms
        if action == 'login':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        elif action == 'register':
            username = request.POST['username']
            email = request.POST['email']
            password1 = request.POST['password1']
            password2 = request.POST['password2']
            if password1 != password2:
                messages.error(request, 'Passwords do not match.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1
                )
                messages.success(
                    request,
                    'Account created! You can now log in.'
                )
    return render(request, 'login.html')


def chat_bot_view(request):
    user_message = request.GET.get("message", "").lower()

    # Simple conditions

    if "hello" in user_message:
        reply = "Hi there! How can I help you?"
    elif "bye" in user_message:
        reply = "Goodbye! Have a great day!"
    else:
        reply = f"You said: {user_message}"

    return JsonResponse({"reply": reply})


def chat_bot_page(request):
    return render(request, 'main/chatbot.html')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'content', 'rating']


def reviews_page(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reviews_page')
    else:
        form = ReviewForm()

    reviews = Review.objects.all().order_by('-created_at')
    return render(
        request,
        'main/reviews.html',
        {'reviews': reviews, 'form': form}
    )

def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    email = request.POST.get("email") or request.GET.get("email")

    if request.method == "GET":
        return render(
            request,
            "main/delete_confirm.html",
            {
                "review": review,
                "email": email
            }
        )

    if request.method == "POST":
        if email == review.email:
            review.delete()
            return redirect("review_manage")

        return render(
            request,
            "main/delete_confirm.html",
            {
                "review": review,
                "email": email,
                "error": "Email does not match the author of this review."
            }
        )


def review_manage(request):
    if request.method == "POST":
        email = request.POST.get("email")
        reviews = Review.objects.filter(email=email)

        return render(
            request,
            "main/review_manage_list.html",
            {
                "reviews": reviews,
                "email": email
            }
        )

    return render(request, "main/review_manage.html")

def blog(request):
    posts = BlogPost.objects.filter(is_published=True)

    return render(
        request, 
        'main/blog.html',
        {
            'posts': posts,
        }
    )


def career(request):
    return render(request, 'main/career.html')


def contact(request):
    return render(request, 'main/contact.html')
