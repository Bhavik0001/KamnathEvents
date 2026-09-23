from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import User
from .models import Contact
from .models import Admin
from .models import Subscribe
from .models import Event
from .models import Category
from .models import Booking

def events(request):
    events = Event.objects.all()

    booking_success = request.session.pop(
        "booking_success",
        None
    )

    return render(
        request,
        "events.html",
        {
            "events": events,
            "booking_success": booking_success
        }
    )

def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')

# ADMIN LOGIN
def admin(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("admin_dashboard")

        else:
            error = "Invalid username or password."

    return render(request, "adminlogin.html", {
        "error": error
    })


# ADMIN DASHBOARD
def dashboard(request):
    events = Event.objects.all()
    categories = Category.objects.all()
    contacts = Contact.objects.all().order_by("-id")
    bookings = Booking.objects.select_related("user", "event").order_by("-id")
    users = User.objects.all().order_by("-id")
    return render(request, "dashboard.html", {
        "events": events,
        "categories": categories,
        "contacts": contacts,
        "bookings": bookings,
        "users": users
    })

# LOGOUT
def admin_logout(request):
    logout(request)
    return redirect("admin_login")
# ==========================
# USER SIGNUP AND LOGIN
# ==========================

def index(request):

    error = None
    success = None

    if request.method == "POST":

        form_type = request.POST.get("form_type")

        # =====================
        # SIGNUP
        # =====================

        if form_type == "signup":

            name = request.POST.get("name")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:

                error = "Passwords do not match."

            elif User.objects.filter(email=email).exists():

                error = "Email already registered."

            else:

                user = User.objects.create(
                    name=name,
                    email=email,
                    password=password
                )

                request.session["user_id"] = user.id
                request.session["user_name"] = user.name

                return redirect("events")

        # =====================
        # LOGIN
        # =====================

        elif form_type == "login":

            email = request.POST.get("email")
            password = request.POST.get("password")

            user = User.objects.filter(
                email=email,
                password=password
            ).first()

            if user:

                request.session["user_id"] = user.id
                request.session["user_name"] = user.name

                return redirect("events")

            else:

                error = "Invalid email or password."

    return render(
        request,
        "index.html",
        {
            "error": error,
            "success": success
        }
    )
# CONTACT FORM

def contact(request):

    success = None

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        success = "Your message has been sent successfully!"

    return render(
        request,
        "contact.html",
        {
            "success": success
        }
    )

# ADMIN LOGIN 
  
def admin(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            # Admin table se details check karega
            admin_user = Admin.objects.get(
                name=username,
                password=password
            )

            # Session me admin details save
            request.session["admin_id"] = admin_user.id
            request.session["admin_name"] = admin_user.name

            # Dashboard par redirect
            return redirect("admin_dashboard")

        except Admin.DoesNotExist:
            error = "Invalid username or password."

    return render(
        request,
        "adminlogin.html",
        {
            "error": error
        }
    )

# SUBSCRIBE FORM
def subscribe(request):

    if request.method == "POST":

        email = request.POST.get("email")

        if email:
            if not Subscribe.objects.filter(email=email).exists():

                Subscribe.objects.create(
                    email=email
                )

                request.session["subscribe_success"] = "Successfully subscribed!"

            else:
                request.session["subscribe_error"] = "This email is already subscribed."

    return redirect(request.META.get("HTTP_REFERER", "index"))

# ==========================
# ADD NEW EVENT
# ==========================

def add_event(request):

    if request.method =="POST":

        title = request.POST.get("title")

        category_id = request.POST.get("category")
        
        event_date = request.POST.get("event_date")

        venue = request.POST.get("venue")

        price = request.POST.get("price")

        image = request.FILES.get("image")

        description = request.POST.get("description")

        #FIND CATEGORY OBJECT

        category = Category.objects.get(
            id=category_id
        )

        #EVENT DATABASE MAI STORE KAREGA

        Event.objects.create(
            title=title,

            category=category,

            event_date=event_date,

            venue=venue,

            price=price,

            image=image,

            description=description
        )
        return redirect("admin_dashboard")

    return redirect("admin_dashboard")

# ==========================
# EDIT EVENT
# ==========================

def edit_event(request, id):

    event = Event.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == "POST":

        event.title = request.POST.get("title")

        category_id = request.POST.get("category")
        event.category = Category.objects.get(id=category_id)

        event.event_date = request.POST.get("event_date")

        event.venue = request.POST.get("venue")

        event.price = request.POST.get("price")

        # Image update only if new image selected
        if request.FILES.get("image"):
            event.image = request.FILES.get("image")

        event.description = request.POST.get("description")

        event.save()

        return redirect("admin_dashboard")

    return render(
        request,
        "dashboard.html",
        {
            "edit_event": event,
            "categories": categories,
            "events": Event.objects.all()
        }
    )
# ==========================
# DELETE EVENT
# ==========================

def delete_event(request, id):

    event = Event.objects.get(id=id)

    event.delete()

    return redirect("admin_dashboard")

# ==========================
# ADD CATEGORY
# ==========================

def add_category(request):

    if request.method == "POST":

        category_name = request.POST.get("category_name")

        if category_name:
            Category.objects.get_or_create(
                category_name=category_name
            )

    return redirect("admin_dashboard")


# ==========================
# EDIT CATEGORY
# ==========================

def edit_category(request, id):

    category = Category.objects.get(id=id)

    if request.method == "POST":

        category_name = request.POST.get("category_name")

        if category_name:
            category.category_name = category_name
            category.save()

        return redirect("admin_dashboard")

    return redirect("admin_dashboard")


# ==========================
# DELETE CATEGORY
# ==========================

def delete_category(request, id):

    category = Category.objects.get(id=id)

    category.delete()

    return redirect("admin_dashboard")

# ==========================
# BOOK EVENT
# ==========================

def book_event(request, event_id):

    print("====================================")
    print("BOOK EVENT CALLED")
    print("SESSION:", dict(request.session))
    print("USER ID:", request.session.get("user_id"))
    print("EVENT ID:", event_id)
    print("====================================")

    if "user_id" not in request.session:
        return redirect("index")

    user_id = request.session.get("user_id")

    user = User.objects.get(id=user_id)

    event = Event.objects.get(id=event_id)

    Booking.objects.create(
        user=user,
        event=event,
        booking_date=timezone.now().date(),
        status="Confirmed"
    )

    request.session["booking_success"] = "Ticket Booked Successfully!"

    return redirect("events")

# ==========================
# APPROVE BOOKING
# ==========================

def approve_booking(request, booking_id):

    if request.method == "POST":

        booking = Booking.objects.get(id=booking_id)

        booking.status = "Confirmed"
        booking.save()

    return redirect("admin_dashboard")

# ==========================
# CANCEL BOOKING
# ==========================

def cancel_booking(request, booking_id):

    if request.method == "POST":

        booking = Booking.objects.get(id=booking_id)

        booking.status = "Cancelled"
        booking.save()

    return redirect("admin_dashboard")

