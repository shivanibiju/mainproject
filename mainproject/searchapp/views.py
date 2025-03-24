from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Seeker, Talent, SearchHistory, TalentCategory, ProfilePicture, TalentLogin
from .forms import SeekerForm, LoginForm, TalentForm, TLoginForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
import re
import nltk
from nltk.corpus import stopwords


def index(request):
    return render(request, 'index.html')

def styles(request):
    return render(request, 'styles.html')


# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')


def normal_search_view(request):
    categories = TalentCategory.objects.all()

    # Get distinct gender and address values
    genders = Talent.objects.values_list('gender', flat=True).distinct()
    addresses = Talent.objects.values_list('address', flat=True).distinct()

    return render(request, 'normal_search.html', {
        'categories': categories,
        'genders': genders,
        'addresses': addresses,
    })



def normal_search_results(request):
    # Fetch all categories to populate the dropdown
    categories = TalentCategory.objects.all()

    # Initialize filters dictionary
    filters = {}

    # Initialize variables to store selected filters
    selected_category = None
    selected_gender = None
    selected_location = None
    talents = None

    # Retrieve the filter values from the form
    if request.method == 'POST':
        selected_category = request.POST.get('category')
        selected_gender = request.POST.get('gender')
        selected_location = request.POST.get('location')

        min_age = request.POST.get('min_age')
        max_age = request.POST.get('max_age')
        min_height = request.POST.get('min_height')
        max_height = request.POST.get('max_height')
        min_weight = request.POST.get('min_weight')
        max_weight = request.POST.get('max_weight')
        min_experience = request.POST.get('experience')

        # Initialize filter conditions
        filter_conditions = Q()

        # Apply gender filter
        if selected_gender:
            filter_conditions &= Q(gender=selected_gender)
            filters['Gender'] = selected_gender

        # Apply category filter
        if selected_category:
            filter_conditions &= Q(skillprofile__talent_category_id=selected_category)
            filters['Category'] = TalentCategory.objects.get(id=selected_category).category_name

        # Apply location filter
        if selected_location:
            filter_conditions &= Q(address=selected_location)
            filters['Location'] = selected_location

        # Apply min/max age filters
        if min_age:
            filter_conditions &= Q(age__gte=min_age)
            filters['Min Age'] = min_age
        if max_age:
            filter_conditions &= Q(age__lte=max_age)
            filters['Max Age'] = max_age

        # Apply min/max height filters
        if min_height:
            filter_conditions &= Q(height_in_cm__gte=min_height)
            filters['Min Height'] = min_height
        if max_height:
            filter_conditions &= Q(height_in_cm__lte=max_height)
            filters['Max Height'] = max_height

        # Apply min/max weight filters
        if min_weight:
            filter_conditions &= Q(weight_in_kg__gte=min_weight)
            filters['Min Weight'] = min_weight
        if max_weight:
            filter_conditions &= Q(weight_in_kg__lte=max_weight)
            filters['Max Weight'] = max_weight

        # Apply experience filter
        if min_experience:
            filter_conditions &= Q(experience__gte=min_experience)
            filters['Min Experience'] = min_experience

        # Fetch talents based on the filter conditions
        talents = Talent.objects.filter(filter_conditions).distinct()

        # Print the applied filters in the Python terminal (for debugging purposes)
        if filters:
            print("Applied Filters:")
            for filter_name, filter_value in filters.items():
                print(f"{filter_name}: {filter_value}")

    # Return the filtered results to the template, including the categories, gender, location, and selected filters
    return render(request, 'normal_search.html', {
        'categories': categories,
        'genders': Talent.objects.values_list('gender', flat=True).distinct(),  # Get all distinct genders
        'addresses': Talent.objects.values_list('address', flat=True).distinct(),  # Get all distinct locations
        'talents': talents,
        'selected_category': selected_category,
        'selected_gender': selected_gender,
        'selected_location': selected_location,
    })

#Seeker registration
def register_view(request):
    if request.method == 'POST':
        form = SeekerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect after successful registration
    else:
        form = SeekerForm()

    return render(request, 'register.html', {'form': form})

#Seeker login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                seeker = Seeker.objects.get(username=username)

                if seeker.password == password:
                    request.session['seeker_id'] = seeker.id
                    return redirect('search')  # Redirect to the search page or dashboard
                else:
                    messages.error(request, 'Incorrect password.')
            except Seeker.DoesNotExist:
                messages.error(request, 'User does not exist.')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

#Talent registration
def t_register_view(request):
    if request.method == 'POST':
        form = TalentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('t_login')  # Redirect after successful registration
    else:
        form = TalentForm()

    return render(request, 't_register.html', {'form': form})


from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from .forms import TLoginForm
from .models import TalentLogin


def t_login_view(request):
    if request.method == 'POST':
        form = TLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                # Check if the user already exists in the Django auth system
                user = User.objects.get(username=username)

                # If the user exists, authenticate with the password
                if user.check_password(password):
                    login(request, user)  # Log the user in
                    return redirect('t_home')  # Redirect to home page
                else:
                    messages.error(request, 'Invalid username or password.')
            except User.DoesNotExist:
                # If the user doesn't exist, check the TalentLogin model
                try:
                    talent = TalentLogin.objects.get(username=username)

                    # Check the password in TalentLogin model
                    if talent.password == password:  # Assuming password is not hashed
                        # Create the Django user
                        user = User.objects.create_user(username=username, password=password)
                        login(request, user)  # Log the user in

                        # Redirect to the home page
                        return redirect('t_home')
                    else:
                        messages.error(request, 'Invalid username or password.')
                except TalentLogin.DoesNotExist:
                    messages.error(request, 'Invalid username or password.')
    else:
        form = TLoginForm()

    return render(request, 't_login.html', {'form': form})


#Free-text search
def search_view(request):
    if request.method == 'POST':
        search_query = request.POST.get('query', '')

        # Store the search query in the SearchHistory model
        SearchHistory.objects.create(query=search_query)

        # Optionally, store the query in the session for further use
        request.session['last_search'] = search_query

        # Process the search query to extract filters (e.g., age, gender, etc.)
        filters = interpret_query(search_query)

        # Process the search query (extract filters and search)
        results = build_dynamic_query(filters)

        # Return the results to the template
        return render(request, 'search.html', {'search_query': search_query, 'results': results})

    return render(request, 'search.html')


from textblob import TextBlob
import re
from nltk.corpus import stopwords

# A predefined whitelist of terms that should not be corrected
WHITELIST_TERMS = {"dubbing","kochi"}

def correct_term(term):
    """Corrects spelling of a term, unless it's in the whitelist."""
    # If the term is in the whitelist, don't apply any corrections
    if term.lower() in WHITELIST_TERMS:
        return term
    # Otherwise, apply spell correction using TextBlob
    return str(TextBlob(term).correct())

def interpret_query(query):
    # # Perform spell correction on the query
    # blob = TextBlob(query)
    # corrected_query = str(blob.correct())

    corrected_query = correct_term(query)

    # Get the stopwords from nltk
    STOPWORDS = set(stopwords.words('english'))

    # Gender search pattern
    gender = re.search(r'\b(male|female|man|woman|boy|girl|males|females|women|men)\b', corrected_query, re.IGNORECASE)

    # Age range search pattern
    age_range = re.search(
        r'\bage\s*(>=|<=|>|<|under|is under|over|is over|between|is between|above|is above|below|is below)?\s*(\d+)(?:\s*and\s*(\d+))?',
        corrected_query, re.IGNORECASE
    )

    # Height range search pattern
    height_range = re.search(
        r'\bheight\s*(>=|<=|>|<|between|is between|above|is above|below|is below)?\s*(\d+)(?:\s*and\s*(\d+))?\s*(cm)?\b',
        corrected_query, re.IGNORECASE
    )

    # Weight range search pattern
    weight_range = re.search(
        r'\bweight\s*(>=|<=|>|<|between|is between|above|is above|below|is below)?\s*(\d+)(?:\s*and\s*(\d+))?\s*(kg)?\b',
        corrected_query, re.IGNORECASE
    )

    # Address search pattern
    address = re.search(r'\b(?:living in|lives in|located in|address is)\s*([\w\s]+)', corrected_query, re.IGNORECASE)

    # Profession search pattern
    profession = re.search(r'\b(?:male|female|who is an|who is a|who is|profession is|works as)\s+(\w+)', query,
                           re.IGNORECASE)

    # Experience search pattern
    experience = re.search(r'\bexperience\s*(>=|<=|>|<|more\s*than|less\s*than|over|under)?\s*(\d+)\s*(years?|yrs?)\b',
                           corrected_query, re.IGNORECASE)

    # Extract descriptive terms excluding stopwords
    words = query.split()
    descriptive_terms = [
        correct_term(word.lower()) for word in words if word.lower() not in STOPWORDS and len(word) > 2
    ]

    # Initialize filters
    filters = {
        'age': None,
        'gender': gender.group(0).lower() if gender else None,
        'height': None,
        'weight': None,
        'profession': profession.group(1).strip() if profession else None,
        'experience': None,
        'experience_comparator': None,
        'address': address.group(1).strip() if address else None,
        'descriptions': descriptive_terms,
    }

    # Age filter logic
    if age_range:
        operator = age_range.group(1)
        if operator in ["under", "<"]:
            filters["age"] = ("<", int(age_range.group(2)))
        elif operator in ["is under", "<"]:
            filters["age"] = ("<", int(age_range.group(2)))
        elif operator in ["below", "<"]:
            filters["age"] = ("<", int(age_range.group(2)))
        elif operator in ["is below", "<"]:
            filters["age"] = ("<", int(age_range.group(2)))
        elif operator in ["over", ">"]:
            filters["age"] = (">", int(age_range.group(2)))
        elif operator in ["is over", ">"]:
            filters["age"] = (">", int(age_range.group(2)))
        elif operator in ["above", ">"]:
            filters["age"] = (">", int(age_range.group(2)))
        elif operator in ["is above", ">"]:
            filters["age"] = (">", int(age_range.group(2)))
        elif operator == "between" and age_range.group(3):
            filters["age"] = (int(age_range.group(2)), int(age_range.group(3)))
        elif operator == "is between" and age_range.group(3):
            filters["age"] = (int(age_range.group(2)), int(age_range.group(3)))
        else:
            filters["age"] = ("=", int(age_range.group(2)))

    # Height filter logic
    if height_range:
        operator = height_range.group(1)
        if operator in ["below", "<"]:
            filters["height"] = ("<", int(height_range.group(2)))
        elif operator in ["is below", "<"]:
            filters["height"] = ("<", int(height_range.group(2)))
        elif operator == "above" and height_range.group(2):
            filters["height"] = (">", int(height_range.group(2)))
        elif operator == "is above" and height_range.group(2):
            filters["height"] = (">", int(height_range.group(2)))
        elif operator == "between" and height_range.group(3):
            filters["height"] = (int(height_range.group(2)), int(height_range.group(3)))
        elif operator == "is between" and height_range.group(3):
            filters["height"] = (int(height_range.group(2)), int(height_range.group(3)))
        else:
            filters["height"] = ("=", int(height_range.group(2)))

    # Weight filter logic
    if weight_range:
        operator = weight_range.group(1)
        if operator in ["below", "<"]:
            filters["weight"] = ("<", int(weight_range.group(2)))
        elif operator in ["is below", "<"]:
            filters["weight"] = ("<", int(weight_range.group(2)))
        elif operator == "above" and weight_range.group(2):
            filters["weight"] = (">", int(weight_range.group(2)))
        elif operator == "is above" and weight_range.group(2):
            filters["weight"] = (">", int(weight_range.group(2)))
        elif operator == "between" and weight_range.group(3):
            filters["weight"] = (int(weight_range.group(2)), int(weight_range.group(3)))
        elif operator == "is between" and weight_range.group(3):
            filters["weight"] = (int(weight_range.group(2)), int(weight_range.group(3)))
        else:
            filters["weight"] = ("=", int(weight_range.group(2)))

    # Experience filter logic
    if experience:
        operator = experience.group(1)
        years = int(experience.group(2))

        if operator in ["more than", "over"]:
            filters["experience_comparator"] = "more than"
            filters["experience"] = years
        elif operator in ["less than", "under"]:
            filters["experience_comparator"] = "less than"
            filters["experience"] = years
        elif operator in [">", "greater than"]:
            filters["experience_comparator"] = "more than"
            filters["experience"] = years
        elif operator in ["<", "less than"]:
            filters["experience_comparator"] = "less than"
            filters["experience"] = years
        elif operator == "between" and experience.group(3):
            filters["experience_comparator"] = "between"
            filters["experience"] = (years, int(experience.group(3)))
        else:
            filters["experience_comparator"] = "="
            filters["experience"] = years

    return filters



def build_dynamic_query(filters):
    """Constructs a dynamic query based on filters and fetches profiles from the database."""
    query = Q()

    print("Filters:", filters)

    # Handle gender
    if filters.get("gender"):
        gender = filters["gender"].rstrip("s").lower()  # Normalize plural genders and lowercase
        if gender in ["male", "man", "boy"]:
            query &= Q(gender__iexact="male")
        elif gender in ["female", "woman", "girl"]:
            query &= Q(gender__iexact="female")
        else:
            query &= Q(gender__iexact=gender)

    # Handle age
    if filters.get("age"):
        age_filter = filters["age"]
        if isinstance(age_filter, tuple):
            if len(age_filter) == 2 and isinstance(age_filter[0], int):
                query &= Q(age__gte=age_filter[0], age__lte=age_filter[1])
            elif age_filter[0] == "<":
                query &= Q(age__lt=age_filter[1])
            elif age_filter[0] == ">":
                query &= Q(age__gt=age_filter[1])
        elif isinstance(age_filter, int):
            query &= Q(age=age_filter)

    # Handle height
    if filters.get("height"):
        height_filter = filters["height"]
        if isinstance(height_filter, tuple):
            if len(height_filter) == 2 and isinstance(height_filter[0], int):
                query &= Q(height_in_cm__gte=height_filter[0], height_in_cm__lte=height_filter[1])
            elif height_filter[0] == "<":
                query &= Q(height_in_cm__lt=height_filter[1])
            elif height_filter[0] == ">":
                query &= Q(height_in_cm__gt=height_filter[1])
        elif isinstance(height_filter, int):
            query &= Q(height_in_cm=height_filter)

    # Handle weight
    if filters.get("weight"):
        weight_filter = filters["weight"]
        if isinstance(weight_filter, tuple):
            if len(weight_filter) == 2 and isinstance(weight_filter[0], int):
                query &= Q(weight_in_kg__gte=weight_filter[0], weight_in_kg__lte=weight_filter[1])
            elif weight_filter[0] == "<":
                query &= Q(weight_in_kg__lt=weight_filter[1])
            elif weight_filter[0] == ">":
                query &= Q(weight_in_kg__gt=weight_filter[1])
        elif isinstance(weight_filter, int):
            query &= Q(weight_in_kg=weight_filter)

    # Handle experience
    if filters.get("experience"):
        experience_filter = filters["experience"]
        if isinstance(experience_filter, tuple):
            query &= Q(experience__gte=experience_filter[0],
                        experience__lte=experience_filter[1])  # Experience between two values
        else:
            query &= Q(experience=experience_filter)

    # Handle address
    if filters.get("address"):
        # Apply spell correction to address term, except for whitelist terms
        corrected_address = correct_term(filters["address"])
        query &= Q(address__icontains=corrected_address)

    # Handle profession
    if filters.get("profession"):
        # Apply spell correction to profession term, except for whitelist terms
        corrected_profession = correct_term(filters["profession"])
        query &= Q(skillprofile__talent_category__category_name__icontains=corrected_profession)

    # Handle descriptive terms
    if filters.get("descriptions"):
        for term in filters["descriptions"]:
            # Apply spell correction to each term, except for whitelist terms
            corrected_term = correct_term(term)

            # # Use regex with word boundaries (\b) to ensure we match the term as a whole word
            # query |= (
            #         Q(talent_description__regex=r'\b' + re.escape(corrected_term) + r'\b') |
            #         Q(skillprofile__achievements__regex=r'\b' + re.escape(corrected_term) + r'\b') |
            #         Q(skillprofile__talent_category__category_name__regex=r'\b' + re.escape(corrected_term) + r'\b')
            # )

    # Now apply the query to the Talent model to fetch the matching profiles
    results = Talent.objects.filter(query)

    print("Constructed Query:", query)

    return results




#Talent profile
from django.shortcuts import render, redirect, get_object_or_404
from .models import Talent, SkillProfile, TalentLogin
from .forms import TalentProfileForm, SkillProfileForm
from django.contrib import messages

@login_required
def t_home(request):
    if not request.user.is_authenticated:
        print("User is not logged in.")
        return redirect('t_login')

    print(f"Logged in user: {request.user.username}")

    try:
        talent_login = TalentLogin.objects.get(username=request.user.username)
        talent = talent_login.talent
    except TalentLogin.DoesNotExist:
        return redirect('t_login')

    skill_profiles = SkillProfile.objects.filter(talent=talent)

    talent_form = TalentProfileForm(instance=talent)
    skill_form = SkillProfileForm()

    if request.method == 'POST':
        print(f"POST data: {request.POST}")

        # Handle profile editing
        if 'edit_profile' in request.POST:
            # Show the edit form for talent profile
            return render(request, 't_home.html', {
                'talent': talent,
                'talent_form': talent_form,
                'skill_profiles': skill_profiles,
                'skill_form': skill_form,
                'editing_talent': True,
            })

        # Handle saving the edited talent profile
        elif 'save_profile' in request.POST:
            talent_form = TalentProfileForm(request.POST, instance=talent)
            if talent_form.is_valid():
                talent_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('t_home')
            else:
                print("Form errors:", talent_form.errors)
                messages.error(request, "There was an error with the form. Please check your inputs.")

        # Handle profile deletion
        elif 'delete_profile' in request.POST:
            talent.delete()
            messages.success(request, "Profile deleted successfully.")
            return redirect('logout')

        # Handle adding a new skill profile
        elif 'add_skill_profile' in request.POST:
            skill_form = SkillProfileForm(request.POST)
            if skill_form.is_valid():
                skill_profile = skill_form.save(commit=False)
                skill_profile.talent = talent
                skill_profile.save()
                messages.success(request, "Skill profile added successfully.")
                return redirect('t_home')

        # Handle editing an existing skill profile
        elif 'edit_skill_profile' in request.POST:
            skill_id = request.POST.get('edit_skill_profile')
            print(f"Editing skill profile with ID: {skill_id}")

            if not skill_id:
                messages.error(request, "No skill ID provided for editing.")
                return redirect('t_home')

            try:
                skill_profile = SkillProfile.objects.get(id=skill_id, talent=talent)
                skill_form = SkillProfileForm(instance=skill_profile)
                return render(request, 't_home.html', {
                    'talent': talent,
                    'talent_form': talent_form,
                    'skill_profiles': skill_profiles,
                    'skill_form': skill_form,
                    'edit_skill_id': skill_id,
                    'editing_skill': True,
                })
            except SkillProfile.DoesNotExist:
                messages.error(request, "Skill profile not found.")
            except Exception as e:
                print(f"Error editing skill profile: {str(e)}")
                messages.error(request, f"Error editing skill profile: {str(e)}")

            return redirect('t_home')

        # Handle saving an edited skill profile
        elif 'save_skill_profile' in request.POST:
            skill_id = request.POST.get('skill_id')

            if not skill_id:
                messages.error(request, "No skill ID provided for saving.")
                return redirect('t_home')

            try:
                skill_profile = SkillProfile.objects.get(id=skill_id, talent=talent)
                skill_form = SkillProfileForm(request.POST, instance=skill_profile)

                if skill_form.is_valid():
                    skill_form.save()
                    messages.success(request, "Skill profile updated successfully.")
                else:
                    print(f"Skill form errors: {skill_form.errors}")
                    messages.error(request, f"Form validation errors: {skill_form.errors}")
            except Exception as e:
                print(f"Error saving skill profile: {str(e)}")
                messages.error(request, f"Error saving skill profile: {str(e)}")

            return redirect('t_home')

        # Handle deleting an existing skill profile
        elif 'delete_skill_profile' in request.POST:
            skill_id = request.POST.get('delete_skill_profile')
            print(f"Deleting skill profile with ID: {skill_id}")

            if not skill_id:
                messages.error(request, "No skill ID provided for deletion.")
                return redirect('t_home')

            try:
                skill_profile = SkillProfile.objects.get(id=skill_id, talent=talent)
                skill_profile.delete()
                messages.success(request, "Skill profile deleted successfully.")
            except SkillProfile.DoesNotExist:
                messages.error(request, "Skill profile not found.")
            except Exception as e:
                print(f"Error deleting skill profile: {str(e)}")
                messages.error(request, f"Error deleting skill profile: {str(e)}")

            return redirect('t_home')

    return render(request, 't_home.html', {
        'talent': talent,
        'talent_form': talent_form,
        'skill_profiles': skill_profiles,
        'skill_form': skill_form,
    })

