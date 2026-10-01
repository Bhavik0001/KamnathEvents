from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import User
from .models import Contact
from .models import Admin
from .models import Subscribe
from .models import Event
from .models import Category
from .models import Booking
from django.db.models import Count, Sum


def events(request):
    events = Event.objects.all()
    categories = Category.objects.all()

    booking_success = request.session.pop(
        "booking_success",
        None
    )

    return render(
        request,
        "events.html",
        {
            "events": events,
            "categories": categories,
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


# ==========================
# ADMIN DASHBOARD
# ==========================
# ==========================
# ADMIN DASHBOARD
# ==========================

def dashboard(request):
    events = Event.objects.all()
    categories = Category.objects.all()
    contacts = Contact.objects.all().order_by("-id")

    bookings = Booking.objects.select_related(
        "user",
        "event"
    ).order_by("-id")

    users = User.objects.annotate(
        total_bookings=Count("booking")
    ).order_by("-id")

    # ==========================
    # DASHBOARD COUNTS
    # ==========================

    total_events = Event.objects.count()
    total_bookings = Booking.objects.count()
    total_customers = User.objects.count()
    new_inquiries = Contact.objects.count()

    # ==========================
    # REPORTS
    # ==========================

    # Total booking value
    total_booking_value = Booking.objects.aggregate(
        total=Sum("event__price")
    )["total"] or 0

    # Event performance
    event_performance = Event.objects.annotate(
        total_bookings=Count("booking")
    ).select_related(
        "category"
    ).order_by("-total_bookings")

    # ==========================
    # ACTIVE SECTION
    # ==========================

    active_section = request.GET.get(
        "section",
        "dashboard"
    )

    return render(request, "dashboard.html", {
        "events": events,
        "categories": categories,
        "contacts": contacts,
        "bookings": bookings,
        "users": users,

        # Dashboard
        "total_events": total_events,
        "total_bookings": total_bookings,
        "total_customers": total_customers,
        "new_inquiries": new_inquiries,

        # Reports
        "total_booking_value": total_booking_value,
        "event_performance": event_performance,

        "active_section": active_section,
    })


# ==========================
# LOGOUT
# ==========================

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
            elif User.objects.filter(name=name).exists() or User.objects.filter(email=email).exists():
                error = "User with this name or email already exists."
            else:
                user = User.objects.create(
                    name=name,
                    email=email,
                    password=password
                )
                error = "You already have an account! Please login."
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


# ==========================
# CONTACT FORM
# ==========================

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


# ==========================
# ADMIN LOGIN
# ==========================

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


# ==========================
# SUBSSCRIBE FORM
# ==========================

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
    if request.method == "POST":
        title = request.POST.get("title")
        category_id = request.POST.get("category")
        event_date = request.POST.get("event_date")
        venue = request.POST.get("venue")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        description = request.POST.get("description")

        category = Category.objects.get(id=category_id)

        Event.objects.create(
            title=title,
            category=category,
            event_date=event_date,
            venue=venue,
            price=price,
            image=image,
            description=description
        )

        return redirect("/dashboard/?section=events")

    return redirect("/dashboard/?section=events")


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

        return redirect("/dashboard/?section=events")

    return render(
        request,
        "dashboard.html",
        {
            "edit_event": event,
            "categories": categories,
            "events": Event.objects.all(),
        }
    )


# ==========================
# DELETE EVENT
# ==========================

def delete_event(request, id):
    event = Event.objects.get(id=id)
    event.delete()
    return redirect("/dashboard/?section=events")


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

    return redirect("/dashboard/?section=categories")


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

        return redirect("/dashboard/?section=categories")

    return redirect("/dashboard/?section=categories")


# ==========================
# DELETE CATEGORY
# ==========================

def delete_category(request, id):
    if request.method == "POST":
        category = Category.objects.get(id=id)
        category.delete()

    return redirect("/dashboard/?section=categories")


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

    # CREATE BOOKING
    booking = Booking.objects.create(
        user=user,
        event=event,
        booking_date=timezone.now().date(),
        status="Confirmed"
    )

    # SUCCESS MESSAGE
    request.session["booking_success"] = "Ticket Booked Successfully!"

    # SAVE BOOKING ID FOR PDF
    request.session["ticket_id"] = booking.id

    return redirect("events")


# ==========================
# APPROVE BOOKING
# ==========================

def approve_booking(request, booking_id):
    if request.method == "POST":
        booking = Booking.objects.get(id=booking_id)
        booking.status = "Confirmed"
        booking.save()

    return redirect("/dashboard/?section=bookings")


# ==========================
# CANCEL BOOKING
# ==========================

def cancel_booking(request, booking_id):
    if request.method == "POST":
        booking = Booking.objects.get(id=booking_id)
        booking.status = "Cancelled"
        booking.save()

    return redirect("/dashboard/?section=bookings")
# ==========================
# DOWNLOAD TICKET
# ==========================


def download_ticket(request, booking_id):
    booking = Booking.objects.get(id=booking_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Kamnath_Event_Ticket_{booking.id}.pdf"'
    )

    pdf = canvas.Canvas(response)

    # =====================================================
    # COLORS
    # =====================================================

    dark_blue = "#111827"
    coral = "#ff563d"
    light_coral = "#fff1ed"
    light_gray = "#f3f4f6"
    gray = "#6b7280"
    white = "#ffffff"
    green = "#16a34a"

    # =====================================================
    # PAGE
    # =====================================================

    page_width = 595
    page_height = 842

    # =====================================================
    # OUTER TICKET BOX
    # =====================================================

    pdf.setFillColor(light_gray)
    pdf.roundRect(
        35,
        90,
        525,
        660,
        18,
        fill=1,
        stroke=0
    )

    # =====================================================
    # HEADER
    # =====================================================

    pdf.setFillColor(dark_blue)
    pdf.roundRect(
        35,
        660,
        525,
        90,
        18,
        fill=1,
        stroke=0
    )

    # Cover bottom rounded corners of header
    pdf.rect(
        35,
        660,
        525,
        35,
        fill=1,
        stroke=0
    )

    # Logo / Brand
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(
        65,
        710,
        "Kamnath"
    )

    pdf.setFillColor(coral)
    pdf.drawString(
        180,
        710,
        "Events"
    )

    # Ticket text
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawRightString(
        530,
        710,
        "EVENT TICKET"
    )

    # Booking ID
    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        65,
        680,
        f"Booking ID: #{booking.id}"
    )

    # =====================================================
    # EVENT TITLE
    # =====================================================

    pdf.setFillColor(dark_blue)
    pdf.setFont("Helvetica-Bold", 18)

    event_title = booking.event.title

    pdf.drawString(
        65,
        625,
        event_title
    )

    # Category badge
    pdf.setFillColor(light_coral)
    pdf.roundRect(
        65,
        585,
        90,
        25,
        12,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(coral)
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawCentredString(
        110,
        593,
        booking.event.category.category_name
    )

    # =====================================================
    # DETAILS AREA
    # =====================================================

    left_x = 65
    right_x = 315

    # Row 1
    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        left_x,
        550,
        "CUSTOMER"
    )

    pdf.drawString(
        right_x,
        550,
        "EMAIL"
    )

    pdf.setFillColor(dark_blue)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        left_x,
        532,
        booking.user.name
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        right_x,
        532,
        booking.user.email
    )

    # Divider
    pdf.setStrokeColor("#e5e7eb")
    pdf.line(
        65,
        510,
        530,
        510
    )

    # Row 2
    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        left_x,
        490,
        "EVENT DATE"
    )

    pdf.drawString(
        right_x,
        490,
        "VENUE"
    )

    pdf.setFillColor(dark_blue)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        left_x,
        472,
        booking.event.event_date.strftime("%d %b %Y")
    )

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        right_x,
        472,
        booking.event.venue
    )

    # Divider
    pdf.setStrokeColor("#e5e7eb")
    pdf.line(
        65,
        450,
        530,
        450
    )

    # Row 3
    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        left_x,
        430,
        "TICKET PRICE"
    )

    pdf.drawString(
        right_x,
        430,
        "BOOKING DATE"
    )

    pdf.setFillColor(coral)
    pdf.setFont("Helvetica-Bold", 14)

    pdf.drawString(
        left_x,
        408,
        f"Rs. {booking.event.price}"
    )

    pdf.setFillColor(dark_blue)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        right_x,
        408,
        booking.booking_date.strftime("%d %b %Y")
    )

    # Divider
    pdf.setStrokeColor("#e5e7eb")
    pdf.line(
        65,
        385,
        530,
        385
    )

    # =====================================================
    # STATUS
    # =====================================================

    pdf.setFillColor(light_coral)
    pdf.roundRect(
        65,
        330,
        465,
        40,
        10,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(gray)
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(
        85,
        345,
        "BOOKING STATUS"
    )

    pdf.setFillColor(green)
    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawRightString(
        510,
        345,
        booking.status
    )

    # =====================================================
    # DESCRIPTION
    # =====================================================

    pdf.setFillColor(dark_blue)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        65,
        295,
        "EVENT DESCRIPTION"
    )

    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 9)

    description = booking.event.description

    # Description ko maximum 2 lines me show karna
    if len(description) > 85:
        line1 = description[:85]
        line2 = description[85:170]
        pdf.drawString(65, 275, line1)
        pdf.drawString(65, 260, line2)
    else:
        pdf.drawString(
            65,
            275,
            description
        )

    # =====================================================
    # FOOTER
    # =====================================================

    pdf.setFillColor(dark_blue)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawCentredString(
        page_width / 2,
        145,
        "Thank you for booking with Kamnath Events!"
    )

    pdf.setFillColor(gray)
    pdf.setFont("Helvetica", 8)

    pdf.drawCentredString(
        page_width / 2,
        125,
        "Please carry this ticket to the event."
    )

    # =====================================================
    # SAVE PDF
    # =====================================================

    pdf.save()

    return response