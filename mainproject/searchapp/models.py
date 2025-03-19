from django.db import models

class ProfilePicture(models.Model):
    picture = models.ImageField(upload_to='profile_pics/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return the name of the image file (not the full path)
        return self.picture.name.split('/')[-1]

    class Meta:
        db_table = 'ProfilePicture'

class TalentCategory(models.Model):
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'TalentCategory'

class Talent(models.Model):
    created_by = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=255)
    modified_date = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15, unique=True)
    age = models.IntegerField()
    experience = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=100)
    height_in_cm = models.FloatField(null=True, blank=True)
    physical_description = models.CharField(max_length=500, null=True, blank=True)
    talent_description = models.CharField(max_length=500)
    weight_in_kg = models.FloatField(null=True, blank=True)
    profile_picture = models.ForeignKey(ProfilePicture, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'Talent'

class SkillProfile(models.Model):
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=100)
    modified_date = models.DateTimeField(auto_now=True)
    achievements = models.CharField(max_length=500, null=True, blank=True)
    experience = models.IntegerField()
    project_details_links = models.BinaryField(null=True, blank=True)
    projects_worked = models.CharField(max_length=500, null=True, blank=True)
    talent_description = models.CharField(max_length=500, null=True, blank=True)
    talent = models.ForeignKey(Talent, on_delete=models.CASCADE)
    talent_category = models.ForeignKey(TalentCategory, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Skill Profile for {self.talent.first_name} {self.talent.last_name}"

    class Meta:
        db_table='SkillProfile'

class Seeker(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    age = models.IntegerField()
    role = models.CharField(max_length=255)

    class Meta:
        db_table = 'seekers'

class SearchHistory(models.Model):
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search Query: {self.query} at {self.timestamp}"

    class Meta:
        db_table = 'SearchHistory'

from django.contrib.auth.models import User
from django.db import models

class TalentLogin(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Plain-text password
    talent = models.ForeignKey('Talent', on_delete=models.CASCADE, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Link to the User model

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'TalentLogin'