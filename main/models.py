from django.db import models

# Create your models here.

# =====================================================
# USERS TABLE
# Signup + User Login
# =====================================================

class User(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100,unique=True)
    password=models.CharField(max_length=255)

    class Meta:
        db_table="users"

    def __str__(self):
        return self.name

# =====================================================
# ADMINS TABLE
# Admin Login
# =====================================================

class Admin(models.Model):
    name=models.CharField(max_length=100)
    password=models.CharField(max_length=255)

    class Meta:
        db_table="admin"
    
    def __str__(self):
        return self.name

# =====================================================
# CATEGORIES TABLE
# =====================================================

class Category(models.Model):
    category_name=models.CharField(max_length=100)

    class Meta:
        db_table="categories"
    
    def __str__(self):
        return self.category_name

# =====================================================
# EVENTS TABLE
# =====================================================
class Event(models.Model):
    title=models.CharField(max_length=100)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    

    event_date=models.DateField()
    venue=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    

    image = models.ImageField(upload_to="events/", blank=True, null=True)
    description=models.TextField()

    class Meta:
        db_table="events"
    
    def __str__(self):
        return self.title

# =====================================================
# BOOKINGS TABLE
# =====================================================
class Booking(models.Model):
    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    event=models.ForeignKey(
        Event,
        on_delete=models.CASCADE
    )

    booking_date=models.DateField()
    status=models.CharField(max_length=20)

    class Meta:
        db_table="bookings"

    def __str__(self):
        return str(self.id)

# =====================================================
# CONTACTS TABLE
# =====================================================

class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    message=models.TextField()

    class Meta:
        db_table="contacts"

    def __str__(self):
        return self.name

class Subscribe(models.Model):
    email=models.EmailField(max_length=100,unique=True)

    class Meta:
        db_table="subscribe"
    
    def __str__(self):
        return self.email