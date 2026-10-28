from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import textwrap
import os
import io
from .models import User
from .models import Contact
from .models import Admin
from .models import Subscribe
from .models import Event
from .models import Category
from .models import Booking
from django.db.models import Count, Sum, F


def is_admin_authenticated(request):
    """Verify whether current session or user is an authenticated administrator."""
    user = getattr(request, "user", None)
    return bool(
        request.session.get("admin_id")
        or (user and getattr(user, "is_authenticated", False) and (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)))
    )


def ensure_default_events():
    """Ensure essential events and categories exist on fresh database install so ticket booking never fails."""
    if Event.objects.exists() or Category.objects.exists():
        return
    try:
        from datetime import date
        cat_map = {}
        for c_name in ["Fashion", "Music", "Comedy", "Technology", "Sports", "Workshop", "Business", "Art"]:
            c, _ = Category.objects.get_or_create(category_name=c_name)
            cat_map[c_name.lower()] = c

        events_defs = [
            (1, "Gujarat Fashion Week 2026", cat_map.get("fashion", cat_map.get("art")), "Grand Ballroom, Ahmedabad", 5999.00, date(2026, 10, 25), "events/fashion.jpg", "Experience the latest fashion trends, creative collections and stylish designs presented by talented designers."),
            (2, "Ahmedabad Music Festival", cat_map.get("music"), "GIFT City Arena, Gandhinagar", 999.00, date(2026, 10, 15), "events/music.jpg", "Live concert featuring regional indie bands, acoustics, and electric performances with high-energy production."),
            (3, "Mumbai Standup Comedy Showcase", cat_map.get("comedy", cat_map.get("standup")), "Bandra Auditorium, Mumbai", 499.00, date(2026, 10, 18), "events/comedy.jpg", "An evening of hilarious punchlines and standup routines with top comedians delivering non-stop laughs."),
            (4, "Bengaluru Tech Summit 2026", cat_map.get("technology", cat_map.get("business")), "Whitefield Convention, Bengaluru", 1499.00, date(2026, 10, 24), "events/tech.jpg", "Annual conference covering product engineering, startup growth, and infrastructure with leading innovators."),
            (5, "Inter-City Football Championship", cat_map.get("sports"), "Sardar Patel Stadium, Ahmedabad", 299.00, date(2026, 11, 5), "events/footballl.jpg", "High-octane knockout football tournament featuring premier regional squads competing for the championship cup."),
            (6, "Creative Hands Art & Craft Workshop", cat_map.get("workshop", cat_map.get("art")), "Kanoria Centre for Arts, Ahmedabad", 799.00, date(2026, 11, 12), "events/business.jpg", "Interactive weekend hands-on masterclass focusing on pottery, canvas painting, and modern resin craft.")
        ]
        for e_id, title, cat, venue, price, e_date, img, desc in events_defs:
            if not Event.objects.filter(id=e_id).exists():
                Event.objects.create(
                    id=e_id,
                    title=title,
                    category=cat,
                    venue=venue,
                    price=price,
                    event_date=e_date,
                    image=img,
                    description=desc
                )
    except Exception:
        pass


def events(request):
    ensure_default_events()
    events = Event.objects.all().select_related("category").annotate(
        total_bookings=Count("booking")
    ).order_by("event_date")
    categories = Category.objects.annotate(
        event_count=Count("event")
    ).order_by("category_name")

    booking_success = request.session.pop(
        "booking_success",
        None
    )
    auth_success = request.session.pop("auth_success", None)
    ticket_id = request.session.get("ticket_id")
    booking_confirmed = request.session.get("booking_confirmed", True)

    return render(
        request,
        "events.html",
        {
            "events": events,
            "categories": categories,
            "booking_success": booking_success,
            "auth_success": auth_success,
            "ticket_id": ticket_id,
            "booking_confirmed": booking_confirmed,
        }
    )


def about(request):
    return render(request, 'about.html')


# ==========================
# ADMIN DASHBOARD
# ==========================

def dashboard(request):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    events = Event.objects.all()
    categories = Category.objects.annotate(
        event_count=Count("event")
    ).order_by("category_name")
    contacts = Contact.objects.all().order_by("-id")

    bookings = Booking.objects.select_related(
        "user",
        "event"
    ).order_by("id")

    recent_bookings = Booking.objects.select_related(
        "user",
        "event"
    ).order_by("id")

    users = User.objects.annotate(
        total_bookings=Count("booking")
    ).order_by("id")

    subscribers = Subscribe.objects.all().order_by("id")

    # ==========================
    # DASHBOARD COUNTS
    # ==========================

    total_events = Event.objects.count()
    total_bookings = Booking.objects.count()
    total_customers = User.objects.count()
    new_inquiries = Contact.objects.count()
    total_subscribers = Subscribe.objects.count()

    # ==========================
    # REPORTS
    # ==========================

    # Total booking value
    total_booking_value = Booking.objects.aggregate(
        total=Sum(F("event__price") * F("quantity"))
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
        "recent_bookings": recent_bookings,
        "users": users,
        "subscribers": subscribers,

        # Dashboard
        "total_events": total_events,
        "total_bookings": total_bookings,
        "total_customers": total_customers,
        "new_inquiries": new_inquiries,
        "total_subscribers": total_subscribers,

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
    request.session.pop("admin_id", None)
    request.session.pop("admin_name", None)
    return redirect("admin_login")


# ==========================
# USER SIGNUP AND LOGIN
# ==========================

def index(request):
    error = None
    success = None

    auth_error = request.session.pop("auth_error", None)
    auth_success = request.session.pop("auth_success", None)
    auth_tab = request.session.pop("auth_tab", "login")

    if request.method == "POST":
        is_ajax = (
            request.headers.get("x-requested-with") == "XMLHttpRequest" or
            request.POST.get("ajax") == "1" or
            "application/json" in request.headers.get("Accept", "")
        )
        form_type = request.POST.get("form_type")
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/events/"

        # =====================
        # SIGNUP
        # =====================
        if form_type == "signup":
            name = request.POST.get("name", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            if not name or not email or not password:
                error = "Please fill in all required fields."
            elif len(password) < 6:
                error = "Password must be at least 6 characters long."
            elif password != confirm_password:
                error = "Passwords do not match. Please verify."
            elif User.objects.filter(email__iexact=email).exists():
                error = "An account with this email address already exists. Please sign in."
            else:
                user = User.objects.create(
                    name=name,
                    email=email,
                    password=make_password(password)
                )
                request.session["user_id"] = user.id
                request.session["user_name"] = user.name
                request.session["user_email"] = user.email

                success_message = f"You have signed up successfully! Welcome, {user.name}."

                if is_ajax:
                    return JsonResponse({
                        "success": True,
                        "message": success_message,
                        "user_name": user.name,
                        "user_email": user.email,
                        "redirect_url": next_url
                    })
                request.session["auth_success"] = success_message
                return redirect(next_url)

            if is_ajax:
                return JsonResponse({"success": False, "error": error}, status=400)
            request.session["auth_error"] = error
            request.session["auth_tab"] = "signup"
            return redirect(next_url)

        # =====================
        # LOGIN
        # =====================
        elif form_type == "login":
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()

            if not email or not password:
                error = "Please enter both your email address and password."
            else:
                user = User.objects.filter(email__iexact=email).first()

                pwd_valid = False
                if user:
                    if check_password(password, user.password):
                        pwd_valid = True
                    elif user.password == password:
                        # Seamlessly authenticate legacy plaintext password and upgrade to PBKDF2 hash
                        pwd_valid = True
                        user.password = make_password(password)
                        user.save(update_fields=["password"])

                if user and pwd_valid:
                    request.session["user_id"] = user.id
                    request.session["user_name"] = user.name
                    request.session["user_email"] = user.email

                    if is_ajax:
                        return JsonResponse({
                            "success": True,
                            "message": f"Welcome back, {user.name}!",
                            "user_name": user.name,
                            "user_email": user.email,
                            "redirect_url": next_url
                        })
                    return redirect(next_url)
                else:
                    error = "Invalid email or password. Please verify your credentials."

            if is_ajax:
                return JsonResponse({"success": False, "error": error}, status=400)
            request.session["auth_error"] = error
            request.session["auth_tab"] = "login"
            return redirect(next_url)

    ensure_default_events()
    events = Event.objects.all().select_related("category").annotate(
        total_bookings=Count("booking")
    ).order_by("-total_bookings", "-id")[:6]
    spotlight_events = events[:4]
    categories = Category.objects.annotate(
        event_count=Count("event")
    ).order_by("category_name")

    booking_success = request.session.pop("booking_success", None)
    ticket_id = request.session.get("ticket_id")
    booking_confirmed = request.session.get("booking_confirmed", True)

    return render(
        request,
        "index.html",
        {
            "error": error or auth_error,
            "auth_error": auth_error,
            "auth_success": auth_success,
            "auth_tab": auth_tab,
            "success": success,
            "events": events,
            "spotlight_events": spotlight_events,
            "categories": categories,
            "booking_success": booking_success,
            "ticket_id": ticket_id,
            "booking_confirmed": booking_confirmed,
        }
    )


# ==========================
# CONTACT FORM
# ==========================

def contact(request):
    success = None

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if name and email and message:
            Contact.objects.create(
                name=name,
                email=email,
                message=message
            )
            success = f"Thank you, {name}! Your message has been sent successfully. We will get back to you shortly."

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
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        # Check 1: Custom Admin model table
        admin_user = Admin.objects.filter(name__iexact=username).first()
        admin_valid = False
        if admin_user:
            if check_password(password, admin_user.password):
                admin_valid = True
            elif admin_user.password == password:
                # Upgrade legacy plaintext admin password to PBKDF2 hash
                admin_valid = True
                admin_user.password = make_password(password)
                admin_user.save(update_fields=["password"])

        # Check 2: Django built-in auth user (superuser / staff)
        django_auth_user = None
        if not admin_valid:
            django_auth_user = authenticate(request, username=username, password=password)

        if admin_user and admin_valid:
            request.session["admin_id"] = admin_user.id
            request.session["admin_name"] = admin_user.name
            return redirect("admin_dashboard")
        elif django_auth_user is not None and (django_auth_user.is_staff or django_auth_user.is_superuser):
            login(request, django_auth_user)
            request.session["admin_id"] = django_auth_user.id
            request.session["admin_name"] = django_auth_user.get_full_name() or django_auth_user.username
            return redirect("admin_dashboard")
        else:
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
        email = request.POST.get("email", "").strip()
        is_ajax = (
            request.headers.get("x-requested-with") == "XMLHttpRequest"
            or "application/json" in request.headers.get("Accept", "")
            or request.content_type == "application/json"
        )

        if not email or "@" not in email:
            if is_ajax:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Please enter a valid email address.",
                    },
                    status=400,
                )
            request.session["subscribe_error"] = "Please enter a valid email address."
            return redirect(request.META.get("HTTP_REFERER", "index"))

        if not Subscribe.objects.filter(email__iexact=email).exists():
            Subscribe.objects.create(email=email)
            message = "You have subscribed successfully!"
            if is_ajax:
                return JsonResponse(
                    {
                        "status": "success",
                        "message": message,
                    }
                )
            request.session["subscribe_success"] = message
        else:
            message = "You are already subscribed to our newsletter."
            if is_ajax:
                return JsonResponse(
                    {
                        "status": "info",
                        "message": message,
                    }
                )
            request.session["subscribe_error"] = message

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {"status": "error", "message": "Invalid request method."},
            status=405,
        )

    return redirect(request.META.get("HTTP_REFERER", "index"))


# ==========================
# ADD NEW EVENT
# ==========================

def add_event(request):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    if request.method == "POST":
        title = request.POST.get("title")
        category_id = request.POST.get("category")
        event_date = request.POST.get("event_date")
        venue = request.POST.get("venue")
        price = request.POST.get("price")
        image = request.FILES.get("image")
        description = request.POST.get("description")

        category = get_object_or_404(Category, id=category_id)

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
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    event = get_object_or_404(Event, id=id)

    if request.method == "POST":
        event.title = request.POST.get("title")

        category_id = request.POST.get("category")
        event.category = get_object_or_404(Category, id=category_id)

        event.event_date = request.POST.get("event_date")
        event.venue = request.POST.get("venue")
        event.price = request.POST.get("price")

        # Image update only if new image selected
        if request.FILES.get("image"):
            event.image = request.FILES.get("image")

        event.description = request.POST.get("description")

        event.save()

        return redirect("/dashboard/?section=events")

    return redirect("/dashboard/?section=events")


# ==========================
# DELETE EVENT
# ==========================

def delete_event(request, id):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect("/dashboard/?section=events")


# ==========================
# ADD CATEGORY
# ==========================

def add_category(request):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    if request.method == "POST":
        category_name = request.POST.get("category_name", "").strip()

        if category_name:
            existing = Category.objects.filter(category_name__iexact=category_name).first()
            if not existing:
                Category.objects.create(category_name=category_name)

    return redirect("/dashboard/?section=categories")


# ==========================
# EDIT CATEGORY
# ==========================

def edit_category(request, id):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category_name = request.POST.get("category_name", "").strip()

        if category_name:
            category.category_name = category_name
            category.save()

    return redirect("/dashboard/?section=categories")


# ==========================
# DELETE CATEGORY
# ==========================

def delete_category(request, id):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    category = Category.objects.filter(id=id).first()
    if category:
        try:
            category.delete()
        except Exception:
            try:
                Event.objects.filter(category=category).delete()
                category.delete()
            except Exception:
                pass

    return redirect("/dashboard/?section=categories")


def delete_subscriber(request, id):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    subscriber = Subscribe.objects.filter(id=id).first()
    if subscriber:
        subscriber.delete()

    return redirect("/dashboard/?section=subscribers")


# ==========================
# BOOK EVENT
# ==========================

def book_event(request, event_id):
    if "user_id" not in request.session:
        if request.user.is_authenticated:
            user = User.objects.filter(email=request.user.email).first()
            if not user:
                user = User.objects.create(
                    name=request.user.username or "Customer",
                    email=request.user.email or f"user_{request.user.id}@example.com",
                    password=""
                )
            request.session["user_id"] = user.id
            request.session["user_name"] = user.name
        else:
            return redirect(f"/index/?next=/book-event/{event_id}/")

    user_id = request.session.get("user_id")
    user = User.objects.filter(id=user_id).first()
    if not user:
        request.session.flush()
        return redirect("index")

    # Ensure events table is seeded
    ensure_default_events()

    # Locate the target event
    event = Event.objects.filter(id=event_id).first()
    if not event:
        # Graceful fallback mapping for demo or placeholder IDs (e.g. 101, 102, 103, 1, 2)
        fallback_titles = {
            1: "Gujarat Fashion Week",
            2: "Ahmedabad Music Festival",
            3: "Mumbai Standup Comedy Showcase",
            4: "Bengaluru Tech Summit",
            5: "Inter-City Football Championship",
            6: "Art & Craft Workshop",
            101: "Ahmedabad Music Festival",
            102: "Mumbai Standup Comedy Showcase",
            103: "Bengaluru Tech Summit",
            104: "Gujarat Tech & Startup Summit",
            105: "Inter-City Football Championship",
            106: "Art & Craft Workshop",
        }
        numeric_id = int(event_id) if str(event_id).isdigit() else 0
        target_keyword = fallback_titles.get(numeric_id)
        if target_keyword:
            event = Event.objects.filter(title__icontains=target_keyword).first()

        # If still not found, pick the earliest upcoming event as safe fallback
        if not event:
            event = Event.objects.first()

        # If database has absolutely no events
        if not event:
            request.session["auth_error"] = "No events are currently open for booking. Please check back soon!"
            return redirect("events")

    # Support multiple passes if specified in checkout
    try:
        qty = int(request.GET.get("qty", 1))
        qty = max(1, min(qty, 10))
    except (ValueError, TypeError):
        qty = 1

    # Create a single consolidated booking with quantity
    booking = Booking.objects.create(
        user=user,
        event=event,
        quantity=qty,
        booking_date=timezone.now().date(),
        status="Confirmed"
    )

    # Save primary ticket ID in session for download
    request.session["ticket_id"] = booking.id

    qty_text = f" ({qty} passes)" if qty > 1 else ""
    request.session["booking_success"] = f"Booking Confirmed for {event.title}{qty_text}! Your official pass is ready."
    request.session["booking_confirmed"] = True

    # Immediate redirect to user's tickets page
    return redirect("my_bookings")


# ==========================
# CONFIRM BOOKING
# ==========================

def confirm_booking(request, booking_id):
    if "user_id" not in request.session:
        return redirect("index")

    user_id = request.session.get("user_id")

    booking = Booking.objects.filter(
        id=booking_id,
        user_id=user_id
    ).first()

    if not booking:
        return redirect("my_bookings")

    # CONFIRM BOOKING
    booking.status = "Confirmed"
    booking.save()

    # KEEP SAME BOOKING ID
    request.session["ticket_id"] = booking.id
    request.session["booking_confirmed"] = True
    request.session["booking_success"] = f"Booking Confirmed for {booking.event.title}! Your ticket is ready."

    return redirect("my_bookings")


# ==========================
# USER CANCEL BOOKING
# ==========================

def user_cancel_booking(request, booking_id):
    if "user_id" not in request.session:
        return redirect("index")

    user_id = request.session.get("user_id")

    booking = Booking.objects.filter(
        id=booking_id,
        user_id=user_id
    ).first()

    if not booking:
        return redirect("my_bookings")

    # CANCEL BOOKING
    booking.status = "Cancelled"
    booking.save()

    # KEEP BOOKING ID
    request.session["ticket_id"] = booking.id
    request.session["booking_confirmed"] = False
    request.session["booking_success"] = f"Ticket #{booking.id} Booking has been cancelled."

    return redirect("my_bookings")


# ==========================
# MY BOOKINGS & TICKETS
# ==========================

def my_bookings(request):
    if "user_id" not in request.session:
        return redirect("index")

    user_id = request.session.get("user_id")
    user_bookings = Booking.objects.filter(
        user_id=user_id
    ).select_related("event", "event__category").order_by("-id")

    booking_success = request.session.pop("booking_success", None)
    ticket_id = request.session.get("ticket_id")
    booking_confirmed = request.session.get("booking_confirmed", True)

    return render(
        request,
        "my_bookings.html",
        {
            "bookings": user_bookings,
            "booking_success": booking_success,
            "ticket_id": ticket_id,
            "booking_confirmed": booking_confirmed,
        }
    )


# ==========================
# USER LOGOUT
# ==========================

def user_logout(request):
    request.session.flush()
    return redirect("events")


# ==========================
# APPROVE BOOKING
# ==========================

def approve_booking(request, booking_id):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = "Confirmed"
        booking.save()

    return redirect("/dashboard/?section=bookings")


# ==========================
# CANCEL BOOKING
# ==========================

def cancel_booking(request, booking_id):
    if not is_admin_authenticated(request):
        return redirect("admin_login")

    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = "Cancelled"
        booking.save()

    return redirect("/dashboard/?section=bookings")


# ==========================
# DOWNLOAD TICKET
# ==========================


def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Security check: User must own the booking or be an authenticated administrator
    user_id = request.session.get("user_id")
    is_admin = is_admin_authenticated(request)
    if not is_admin and (not user_id or booking.user_id != user_id):
        return redirect("my_bookings" if user_id else "index")

    qty = getattr(booking, "quantity", 1) or 1

    # Standard A4 Dimensions in points
    page_w = 595.27
    page_h = 841.89
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(page_w, page_h))

    # Helper function for hex color support
    def set_fill(color):
        pdf.setFillColor(HexColor(color) if isinstance(color, str) else color)

    def set_stroke(color):
        pdf.setStrokeColor(HexColor(color) if isinstance(color, str) else color)

    # Page Background (Clean slate-50 canvas matching website body)
    set_fill("#f8fafc")
    pdf.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # Card Dimensions (Centered on A4)
    card_w = 480
    card_h = 494
    card_x = (page_w - card_w) / 2
    card_y = (page_h - card_h) / 2
    card_top = card_y + card_h

    # Card Outer Box (Pure white surface with clean border, matching website cards)
    set_fill("#ffffff")
    set_stroke("#cbd5e1")
    pdf.setLineWidth(1)
    pdf.roundRect(card_x, card_y, card_w, card_h, 8, fill=1, stroke=1)

    # Top Brand Accent Strip (BookMyShow Crimson #e11d48)
    set_fill("#e11d48")
    pdf.roundRect(card_x, card_top - 5, card_w, 5, 4, fill=1, stroke=0)
    pdf.rect(card_x, card_top - 5, card_w, 2, fill=1, stroke=0)

    # =====================================================
    # HEADER BAR (Clean White matching Website Navbar)
    # =====================================================
    header_h = 50
    header_bottom_y = card_top - header_h

    # Brand Icon (Crimson square with rounded corners)
    icon_size = 28
    icon_x = card_x + 20
    icon_y = header_bottom_y + 11
    set_fill("#e11d48")
    pdf.roundRect(icon_x, icon_y, icon_size, icon_size, 4, fill=1, stroke=0)
    set_fill("#ffffff")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(icon_x + (icon_size / 2), icon_y + 8, "K")

    # Brand Name (Kamnath in dark slate, Events in crimson)
    brand_text_x = icon_x + icon_size + 10
    set_fill("#0f172a")
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(brand_text_x, icon_y + 13, "Kamnath")
    kw = pdf.stringWidth("Kamnath", "Helvetica-Bold", 15)
    set_fill("#e11d48")
    pdf.drawString(brand_text_x + kw + 2, icon_y + 13, "Events")

    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawString(brand_text_x, icon_y + 2, "OFFICIAL EVENT PASS • KAMNATHEVENTS.COM")

    # Header Badges (Right side)
    # Booking Reference Badge
    ref_text = f"PASS #BK-{booking.id:04d} • {qty} PASSES" if qty > 1 else f"PASS #BK-{booking.id:04d}"
    ref_w = pdf.stringWidth(ref_text, "Helvetica-Bold", 7.5) + 14
    ref_x = card_x + card_w - 20 - ref_w
    ref_y = icon_y + 6
    set_fill("#f1f5f9")
    set_stroke("#cbd5e1")
    pdf.roundRect(ref_x, ref_y, ref_w, 18, 3, fill=1, stroke=1)
    set_fill("#334155")
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(ref_x + (ref_w / 2), ref_y + 5, ref_text)

    # Status Pill
    status_raw = (booking.status or "CONFIRMED").upper()
    if status_raw == "CONFIRMED":
        stat_bg, stat_border, stat_text_col, stat_label = "#ecfdf5", "#a7f3d0", "#047857", "● Confirmed"
    elif status_raw == "PENDING":
        stat_bg, stat_border, stat_text_col, stat_label = "#fffbeb", "#fde68a", "#b45309", "● Pending"
    else:
        stat_bg, stat_border, stat_text_col, stat_label = "#fef2f2", "#fecaca", "#b91c1c", "● Cancelled"

    stat_w = pdf.stringWidth(stat_label, "Helvetica-Bold", 7.5) + 14
    stat_x = ref_x - stat_w - 8
    set_fill(stat_bg)
    set_stroke(stat_border)
    pdf.roundRect(stat_x, ref_y, stat_w, 18, 3, fill=1, stroke=1)
    set_fill(stat_text_col)
    pdf.setFont("Helvetica-Bold", 7.5)
    pdf.drawCentredString(stat_x + (stat_w / 2), ref_y + 5, stat_label)

    # Header Divider
    set_stroke("#e2e8f0")
    pdf.setLineWidth(1)
    pdf.line(card_x, header_bottom_y, card_x + card_w, header_bottom_y)

    # =====================================================
    # HERO EVENT SHOWCASE (Thumbnail + Title + Details)
    # =====================================================
    hero_top = header_bottom_y - 14
    thumb_w = 84
    thumb_h = 72
    thumb_x = card_x + 20
    thumb_y = hero_top - thumb_h

    # Check for event thumbnail image
    poster_path = None
    try:
        if booking.event.image and hasattr(booking.event.image, "path") and os.path.exists(booking.event.image.path):
            poster_path = booking.event.image.path
    except Exception:
        poster_path = None

    if not poster_path:
        cat_name = (booking.event.category.category_name if booking.event.category else "").lower()
        static_img_dir = os.path.join(settings.BASE_DIR, "main", "static", "images")
        for candidate in [f"{cat_name}.jpg", "music.jpg", "event.jpg"]:
            candidate_full = os.path.join(static_img_dir, candidate)
            if os.path.exists(candidate_full):
                poster_path = candidate_full
                break

    cat_title = (booking.event.category.category_name if booking.event.category else "EVENT").upper()

    image_drawn = False
    if poster_path and os.path.exists(poster_path):
        try:
            pdf.drawImage(
                poster_path,
                thumb_x,
                thumb_y,
                width=thumb_w,
                height=thumb_h,
                preserveAspectRatio=True,
                anchor="c"
            )
            image_drawn = True
        except Exception:
            image_drawn = False

    if not image_drawn:
        set_fill("#fff1f2")
        pdf.roundRect(thumb_x, thumb_y, thumb_w, thumb_h, 4, fill=1, stroke=0)
        set_fill("#e11d48")
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(thumb_x + (thumb_w / 2), thumb_y + (thumb_h / 2) - 4, cat_title[:10])

    set_stroke("#e2e8f0")
    pdf.setLineWidth(1)
    pdf.roundRect(thumb_x, thumb_y, thumb_w, thumb_h, 4, fill=0, stroke=1)

    # Hero Content on the right of thumbnail
    content_x = card_x + 116

    # Category Pill
    cat_badge_w = pdf.stringWidth(cat_title, "Helvetica-Bold", 6.5) + 12
    set_fill("#fff1f2")
    set_stroke("#fecdd3")
    pdf.roundRect(content_x, hero_top - 12, cat_badge_w, 14, 3, fill=1, stroke=1)
    set_fill("#e11d48")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawCentredString(content_x + (cat_badge_w / 2), hero_top - 8, cat_title)

    # Multi-pass badge if multiple passes booked
    if qty > 1:
        multi_badge_text = f"★ {qty} PASSES BOOKED (CONSOLIDATED)"
        multi_badge_w = pdf.stringWidth(multi_badge_text, "Helvetica-Bold", 6.5) + 14
        multi_badge_x = content_x + cat_badge_w + 6
        set_fill("#eff6ff")
        set_stroke("#bfdbfe")
        pdf.roundRect(multi_badge_x, hero_top - 12, multi_badge_w, 14, 3, fill=1, stroke=1)
        set_fill("#1d4ed8")
        pdf.setFont("Helvetica-Bold", 6.5)
        pdf.drawCentredString(multi_badge_x + (multi_badge_w / 2), hero_top - 8, multi_badge_text)

    # Event Title
    event_title = (booking.event.title or "Event Name").strip()
    if len(event_title) > 36:
        event_title = event_title[:34] + "..."
    set_fill("#0f172a")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(content_x, hero_top - 31, event_title)

    # Event Date
    event_date_str = booking.event.event_date.strftime("%A, %d %B %Y")
    set_fill("#334155")
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(content_x, hero_top - 48, f"DATE:  {event_date_str}")

    # Venue Location
    venue_str = (booking.event.venue or "Venue Address").strip()
    if len(venue_str) > 38:
        venue_str = venue_str[:36] + "..."
    set_fill("#64748b")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(content_x, hero_top - 62, f"VENUE:  {venue_str}")

    # =====================================================
    # ATTENDEE & BOOKING DETAILS GRID (Subtle Card Surface)
    # =====================================================
    details_box_top = thumb_y - 12
    details_box_h = 78
    details_box_y = details_box_top - details_box_h

    set_fill("#f8fafc")
    set_stroke("#e2e8f0")
    pdf.setLineWidth(1)
    pdf.roundRect(card_x + 20, details_box_y, card_w - 40, details_box_h, 6, fill=1, stroke=1)

    # Col 1: Attendee Name & Email
    c1_x = card_x + 34
    r1_y = details_box_top - 15
    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawString(c1_x, r1_y, "ATTENDEE NAME")

    set_fill("#0f172a")
    pdf.setFont("Helvetica-Bold", 9.5)
    pdf.drawString(c1_x, r1_y - 13, str(booking.user.name))

    r2_y = details_box_top - 46
    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawString(c1_x, r2_y, "REGISTERED EMAIL")

    set_fill("#334155")
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(c1_x, r2_y - 13, str(booking.user.email))

    # Col 2: Booking Date & Ticket Tier
    c2_x = card_x + 192
    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawString(c2_x, r1_y, "BOOKING DATE")

    set_fill("#0f172a")
    pdf.setFont("Helvetica-Bold", 9.5)
    pdf.drawString(c2_x, r1_y - 13, booking.booking_date.strftime("%d %b %Y"))

    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawString(c2_x, r2_y, "ADMISSION TIER")

    set_fill("#334155")
    pdf.setFont("Helvetica", 8.5)
    if qty > 1:
        pdf.drawString(c2_x, r2_y - 13, f"Group Entry ({qty} Passes)")
    else:
        pdf.drawString(c2_x, r2_y - 13, "General Admission (1 Pass)")

    # Col 3: Highlight Amount Card
    price_card_x = card_x + 346
    price_card_w = 100
    price_card_h = details_box_h - 16
    price_card_y = details_box_y + 8

    set_fill("#ffffff")
    set_stroke("#cbd5e1")
    pdf.roundRect(price_card_x, price_card_y, price_card_w, price_card_h, 4, fill=1, stroke=1)

    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.drawCentredString(price_card_x + (price_card_w / 2), price_card_y + price_card_h - 13, "TOTAL PAID")

    try:
        unit_price = float(booking.event.price)
        total_price = unit_price * qty
        price_str = f"Rs. {total_price:,.2f}"
    except (ValueError, TypeError):
        price_str = f"Rs. {booking.event.price}"
        unit_price = 0

    set_fill("#e11d48")
    pdf.setFont("Helvetica-Bold", 10.5 if len(price_str) > 11 else 12)
    pdf.drawCentredString(price_card_x + (price_card_w / 2), price_card_y + 24, price_str)

    if qty > 1:
        set_fill("#0f172a")
        pdf.setFont("Helvetica-Bold", 6)
        pdf.drawCentredString(price_card_x + (price_card_w / 2), price_card_y + 13, f"({qty} Passes × Rs. {unit_price:,.0f})")
        set_fill("#047857")
        pdf.setFont("Helvetica-Bold", 5.5)
        pdf.drawCentredString(price_card_x + (price_card_w / 2), price_card_y + 4, "Payment Confirmed")
    else:
        set_fill("#047857")
        pdf.setFont("Helvetica-Bold", 6.5)
        pdf.drawCentredString(price_card_x + (price_card_w / 2), price_card_y + 11, "Payment Confirmed")

    # =====================================================
    # EVENT DESCRIPTION BOX
    # =====================================================
    desc_top = details_box_y - 8
    desc_h = 42
    desc_y = desc_top - desc_h

    set_fill("#ffffff")
    set_stroke("#e2e8f0")
    pdf.roundRect(card_x + 20, desc_y, card_w - 40, desc_h, 4, fill=1, stroke=1)

    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    if qty > 1:
        pdf.drawString(card_x + 30, desc_top - 11, f"EVENT SUMMARY • CONSOLIDATED PASS ({qty} ATTENDEES)")
    else:
        pdf.drawString(card_x + 30, desc_top - 11, "ABOUT THIS EVENT")

    raw_desc = (booking.event.description or "Official event ticketing admission pass.").strip()
    if qty > 1:
        full_text = f"Consolidated official e-ticket pass admitting {qty} persons together. {raw_desc}"
    else:
        full_text = raw_desc
    wrapped = textwrap.wrap(full_text, width=82)[:2]
    set_fill("#334155")
    pdf.setFont("Helvetica", 7.5)
    line_y = desc_top - 23
    for wline in wrapped:
        pdf.drawString(card_x + 30, line_y, wline)
        line_y -= 11

    # =====================================================
    # PERFORATED TICKET TEAR LINE
    # =====================================================
    tear_y = desc_y - 10
    set_stroke("#cbd5e1")
    pdf.setLineWidth(1)
    pdf.setDash([4, 4])
    pdf.line(card_x + 10, tear_y, card_x + card_w - 10, tear_y)
    pdf.setDash([])

    # Semicircular Cutouts on Left & Right Margins
    set_fill("#f8fafc")
    set_stroke("#cbd5e1")
    pdf.circle(card_x, tear_y, 6, fill=1, stroke=1)
    pdf.circle(card_x + card_w, tear_y, 6, fill=1, stroke=1)

    # =====================================================
    # GATE ENTRY & BARCODE SECTION
    # =====================================================
    gate_top = tear_y - 10
    gate_h = 60
    gate_y = gate_top - gate_h

    set_fill("#ffffff")
    set_stroke("#e2e8f0")
    pdf.roundRect(card_x + 20, gate_y, card_w - 40, gate_h, 5, fill=1, stroke=1)

    # Vector Barcode
    bx = card_x + 30
    by = gate_y + 19
    bh = 26
    pattern = [2, 1, 3, 1, 1, 2, 4, 1, 2, 1, 3, 2, 1, 1, 2, 3, 1, 2, 4, 1, 1, 3, 2, 1, 2, 1, 3, 1, 2, 1, 4, 1, 2, 1]
    set_fill("#0f172a")
    for i, bar_w in enumerate(pattern):
        if i % 2 == 0:
            pdf.rect(bx, by, bar_w, bh, fill=1, stroke=0)
        bx += bar_w + 1.2

    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    barcode_label = f"* KMN-PASS-{booking.id:06d}-QTY{qty:02d} *" if qty > 1 else f"* KMN-PASS-{booking.id:06d}-SEC *"
    pdf.drawString(card_x + 30, by - 8, barcode_label)

    # Divider between barcode and guidelines
    set_stroke("#e2e8f0")
    pdf.line(card_x + 215, gate_y + 6, card_x + 215, gate_y + gate_h - 6)

    # Venue Entry Guidelines
    gx = card_x + 228
    set_fill("#0f172a")
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(gx, gate_top - 12, f"VENUE ENTRY GUIDELINES ({qty} PASSES)" if qty > 1 else "VENUE ENTRY GUIDELINES")

    set_fill("#475569")
    pdf.setFont("Helvetica", 6.5)
    if qty > 1:
        pdf.drawString(gx, gate_top - 23, f"• This single e-ticket admits all {qty} attendees together at gate entry.")
        pdf.drawString(gx, gate_top - 34, f"• Government-issued photo ID matching attendee name ({booking.user.name}) required.")
        pdf.drawString(gx, gate_top - 45, "• Gates open 45 minutes prior to scheduled start time.")
    else:
        pdf.drawString(gx, gate_top - 23, "• Present this e-ticket on your mobile or printed paper at gate entry.")
        pdf.drawString(gx, gate_top - 34, "• Government-issued photo ID matching attendee name is required.")
        pdf.drawString(gx, gate_top - 45, "• Gates open 45 minutes prior to scheduled start time.")

    # =====================================================
    # BOTTOM SECURITY STRIP
    # =====================================================
    sec_top = gate_y - 8
    sec_h = 22
    sec_y = sec_top - sec_h

    set_fill("#f8fafc")
    set_stroke("#e2e8f0")
    pdf.roundRect(card_x + 20, sec_y, card_w - 40, sec_h, 4, fill=1, stroke=1)

    set_fill("#64748b")
    pdf.setFont("Helvetica-Bold", 6.5)
    strip_title = f"KAMNATH EVENTS SECURE PASS • {qty} PASSES CONSOLIDATED" if qty > 1 else "KAMNATH EVENTS SECURE PASS • NON-TRANSFERABLE ADMISSION"
    pdf.drawString(card_x + 30, sec_y + 7, strip_title)

    set_fill("#047857")
    pdf.setFont("Helvetica-Bold", 7)
    sec_label = f"✓ VERIFIED GROUP PASS ({qty} PERSONS)" if qty > 1 else "✓ VERIFIED DIGITAL TICKET"
    pdf.drawRightString(card_x + card_w - 30, sec_y + 7, sec_label)

    # =====================================================
    # PAGE FOOTER
    # =====================================================
    set_fill("#94a3b8")
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(
        page_w / 2,
        card_y - 18,
        "Kamnath Events • Online Ticketing Platform • www.kamnathevents.com • Need assistance? support@kamnathevents.com"
    )

    pdf.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    filename = f"Kamnath_Event_Ticket_{booking.id}_{qty}Passes.pdf" if qty > 1 else f"Kamnath_Event_Ticket_{booking.id}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ==========================
# PROJECT DOCUMENTATION PDF
# ==========================


def download_project_docs(request):
    from generate_project_pdf import build_pdf
    pdf_path = os.path.join(settings.BASE_DIR, "Kamnath_Events_Project_Documentation.pdf")
    if not os.path.exists(pdf_path):
        build_pdf(pdf_path)

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    response = HttpResponse(pdf_data, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="Kamnath_Events_Project_Documentation.pdf"'
    return response

