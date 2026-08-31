from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from .models import Contact
from .models import Admin
from .models import Subscribe
def index(request):
    return render(request, 'index.html')


def events(request):
    return render(request, 'events.html')


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
    return render(request, "dashboard.html")


# LOGOUT
def admin_logout(request):
    logout(request)
    return redirect("admin_login")

# USER SIGNUP AND LOGIN
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
                User.objects.create(
                    name=name,
                    email=email,
                    password=password
                )

                success = "Account created successfully!"

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

                success = "Login successful!"

            else:
                error = "Invalid email or password."

    return render(request, "index.html", {
        "error": error,
        "success": success
    })

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