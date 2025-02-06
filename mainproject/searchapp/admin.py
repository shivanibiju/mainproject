from django.contrib import admin
from .models import ProfilePicture
from .models import TalentCategory
from .models import Talent
from .models import SkillProfile
from .models import Seeker

# Register your models here.
@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ('picture', 'uploaded_at')
    list_filter = ('uploaded_at',)

@admin.register(TalentCategory)
class TalentCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)

@admin.register(Talent)
class TalentAdmin(admin.ModelAdmin):
    list_display = ('created_by','created_date','modified_by','modified_date',
                    'first_name','last_name','mobile','age','experience','gender',
                    'height_in_cm','physical_description','talent_description',
                    'weight_in_kg','profile_picture','address')
    search_fields = ('first_name','last_name')
    list_filter = ('created_date','modified_date')

@admin.register(SkillProfile)
class SkillProfileAdmin(admin.ModelAdmin):
    list_display = ('created_by','created_date','modified_by','modified_date',
                    'achievements','experience','project_details_links',
                    'projects_worked','talent_description','talent',
                    'talent_category')
    search_fields = ('talent_category',)
    list_filter = ('created_date','modified_date','talent_category')

@admin.register(Seeker)
class Seeker(admin.ModelAdmin):
    list_display = ('username','password','name','email','mobile','age','role')
    search_fields = ('name',)