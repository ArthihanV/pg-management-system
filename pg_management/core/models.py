from django.db import models
from django.contrib.auth.models import AbstractUser


# -------------------------------
# CUSTOM USER MODEL
# -------------------------------
class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('PG_OWNER', 'PG Owner'),
        ('CUSTOMER', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# -------------------------------
# PG MODEL (MATCHES PGForm)
# -------------------------------
class PG(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pgs'
    )

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    price = models.PositiveIntegerField()
    total_rooms = models.PositiveIntegerField()

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('BOTH', 'Both'),
    )
    gender_type = models.CharField(max_length=10, choices=GENDER_CHOICES)

    image = models.ImageField(upload_to='pg_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    pg = models.ForeignKey(PG, on_delete=models.CASCADE, related_name='rooms')

    ROOM_TYPE_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('TRIPLE', 'Triple'),
    )

    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    price = models.PositiveIntegerField()
    total_rooms = models.PositiveIntegerField()
    available_rooms = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pg.name} - {self.room_type}"
    

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.room}"
