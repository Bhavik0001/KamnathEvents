from decimal import Decimal
from django.db import models

# Create your models here.

# =====================================================
# USERS TABLE
# Signup + User Login
# =====================================================

class User(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.name

# =====================================================
# ADMINS TABLE
# Admin Login
# =====================================================

class Admin(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "admin"
    
    def __str__(self):
        return self.name

# =====================================================
# CATEGORIES TABLE
# =====================================================

class Category(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    category_name = models.CharField(max_length=100)

    class Meta:
        db_table = "categories"
    
    def __str__(self):
        return self.category_name

# =====================================================
# EVENTS TABLE
# =====================================================
class Event(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    event_date = models.DateField()
    venue = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    description = models.TextField()

    class Meta:
        db_table = "events"
    
    def __str__(self):
        return self.title

    @property
    def get_thumbnail_url(self):
        if self.image:
            try:
                img_url = getattr(self.image, "url", None)
                if img_url:
                    return str(img_url)
            except Exception:
                pass

        cat = str(self.category.category_name if self.category else "").lower()
        title_lower = str(self.title or "").lower()

        if "food" in title_lower or "food" in cat or "culinary" in title_lower:
            return "/static/images/food.jpg"
        elif "fashion" in title_lower or "fashion" in cat or "lifestyle" in title_lower:
            return "/static/images/fashion.jpg"
        elif "tech" in title_lower or "workshop" in cat or "web" in title_lower or "code" in title_lower or "develop" in title_lower:
            return "/static/images/tech.jpg"
        elif "comedy" in title_lower or "comedy" in cat or "laugh" in title_lower or "standup" in title_lower:
            return "/static/images/comedy.jpg"
        elif "sport" in title_lower or "sports" in cat or "football" in title_lower or "cricket" in title_lower or "championship" in title_lower:
            return "/static/images/football.jpg"
        elif "music" in title_lower or "music" in cat or "concert" in title_lower or "festival" in title_lower:
            return "/static/images/music.jpg"
        elif "startup" in title_lower or "business" in title_lower or "business" in cat or "summit" in title_lower:
            return "/static/images/business.jpg"
        elif "art" in title_lower or "art" in cat or "exhibit" in title_lower:
            return "/static/images/art.jpg"
        elif "photo" in title_lower or "photography" in cat:
            return "/static/images/photograph.jpg"
        else:
            return "/static/images/event.jpg"

# =====================================================
# BOOKINGS TABLE
# =====================================================
class Booking(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)
    booking_date = models.DateField()
    status = models.CharField(max_length=20)

    class Meta:
        db_table = "bookings"

    def __str__(self):
        return str(getattr(self, "id", self.pk))

    @property
    def total_price(self):
        try:
            event_obj = getattr(self, "event", None)
            price_val = getattr(event_obj, "price", 0) if event_obj else 0
            qty_val = getattr(self, "quantity", 1) or 1
            return Decimal(str(price_val or 0)) * int(qty_val)
        except Exception:
            return Decimal(0)

# =====================================================
# CONTACTS TABLE
# =====================================================

class Contact(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    message = models.TextField()

    class Meta:
        db_table = "contacts"

    def __str__(self):
        return self.name

class Subscribe(models.Model):
    id: int
    DoesNotExist = models.ObjectDoesNotExist
    objects = models.Manager()
    email = models.EmailField(max_length=100, unique=True)

    class Meta:
        db_table = "subscribe"
    
    def __str__(self):
        return self.email