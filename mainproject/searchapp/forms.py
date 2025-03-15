from django import forms
from .models import Seeker, TalentLogin, Talent, SkillProfile


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


class TalentForm(forms.ModelForm):
    class Meta:
        model = TalentLogin
        fields = ['username', 'password']

class TLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())



# Form to edit talent profile
class TalentProfileForm(forms.ModelForm):
    class Meta:
        model = Talent
        fields = ['first_name', 'last_name', 'mobile', 'age', 'experience', 'gender',
                  'height_in_cm', 'physical_description', 'talent_description', 'weight_in_kg', 'address']
        widgets = {
            'age': forms.NumberInput(attrs={'min': 0}),
            'height_in_cm': forms.NumberInput(attrs={'min': 0}),
            'weight_in_kg': forms.NumberInput(attrs={'min': 0}),
        }


# Form to add/edit skill profile
class SkillProfileForm(forms.ModelForm):
    class Meta:
        model = SkillProfile
        fields = ['talent_category', 'achievements', 'experience', 'projects_worked', 'talent_description']
        widgets = {
            'experience': forms.NumberInput(attrs={'min': 0}),
        }
