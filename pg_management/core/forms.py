from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import PG
from .models import Room
from .models import Booking

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PGForm(forms.ModelForm):
    class Meta:
        model = PG
        fields = [
            'name',
            'location',
            'price',
            'total_rooms',
            'gender_type',
            'image'
        ]

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_type',
            'price',
            'total_rooms',
            'available_rooms',
        ]

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in_date']
