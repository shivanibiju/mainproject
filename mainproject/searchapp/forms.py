from django import forms
from .models import Seeker


class SeekerForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('director', 'Director'),
        ('castingagent', 'Casting Agent'),
        ('eventorganizer', 'Event Organizer'),
        ('talentmanager', 'Talent Manager'),
        ('brandrep', 'Brand Representative')
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = Seeker
        fields = ['username', 'password', 'name', 'email', 'mobile', 'age', 'role']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())