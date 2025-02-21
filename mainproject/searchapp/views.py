from django.shortcuts import render, redirect, get_object_or_404
from .models import Seeker, Talent, SearchHistory, TalentCategory
from .forms import SeekerForm, LoginForm
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
import re
import nltk
from nltk.corpus import stopwords

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


def interpret_query(query):
    # Interprets the query to extract structured filters and descriptive terms.

    # Get the stopwords from nltk
    STOPWORDS = set(stopwords.words('english'))

    gender = re.search(r'\b(male|female|man|woman|boy|girl|males|females|women|men)\b', query, re.IGNORECASE)
    age_range = re.search(
        r'\bage\s*(>=|<=|>|<|under|is under|over|is over|between|is between|above|is above|below|is below)?\s*(\d+)(?:\s*and\s*(\d+))?',
        query, re.IGNORECASE
    )
    height_range = re.search(
        r'\bheight\s*(>=|<=|>|<|between|is between|above|is above|below|is below)?\s*(\d+)(?:\s*and\s*(\d+))?\s*(cm)?\b',
        query, re.IGNORECASE
    )
    weight_range = re.search(
        r'\bweight\s*(>=|<=|>|<|between|is between|above|is above|below|is below)?\s*(\d+)(?:\s*and\s*(\d+))?\s*(kg)?\b',
        query, re.IGNORECASE
    )
    address = re.search(r'\b(?:living in|lives in|located in|address is)\s*([\w\s]+)', query, re.IGNORECASE)
    profession = re.search(r'\b(?:male|female|who is an|who is a|profession is|works as)\s+(\w+)', query, re.IGNORECASE)
    experience = re.search(r'\bexperience\s*(>=|<=|>|<|more\s*than|less\s*than|over|under)?\s*(\d+)\s*(years?|yrs?)\b',
                           query, re.IGNORECASE)

    # Extract descriptive terms excluding stopwords
    words = query.split()
    descriptive_terms = [
        word.lower() for word in words if word.lower() not in STOPWORDS and len(word) > 2
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

    if height_range:
        operator = height_range.group(1)
        if operator in ["below", "<"]:
            filters["height"] = ("<", int(height_range.group(2)))
        elif operator in ["is below", "<"]:
            filters["height"] = ("<", int(height_range.group(2)))
        elif operator in ["below", "<"]:
            filters["height"] = ("<", int(height_range.group(2)))
        elif operator in ["above", ">"]:
            filters["height"] = (">", int(height_range.group(2)))
        elif operator in ["is above", ">"]:
            filters["height"] = (">", int(height_range.group(2)))
        elif operator == "between" and height_range.group(3):
            filters["height"] = (int(height_range.group(2)), int(height_range.group(3)))
        elif operator == "is between" and height_range.group(3):
            filters["height"] = (int(height_range.group(2)), int(height_range.group(3)))
        else:
            filters["height"] = ("=", int(height_range.group(2)))

    if weight_range:
        operator = weight_range.group(1)
        if operator in ["below", "<"]:
            filters["weight"] = ("<", int(weight_range.group(2)))
        elif operator in ["is below", "<"]:
            filters["weight"] = ("<", int(weight_range.group(2)))
        elif operator in ["below", "<"]:
            filters["weight"] = ("<", int(weight_range.group(2)))
        elif operator in ["above", ">"]:
            filters["weight"] = (">", int(weight_range.group(2)))
        elif operator in ["is above", ">"]:
            filters["weight"] = (">", int(weight_range.group(2)))
        elif operator == "between" and weight_range.group(3):
            filters["weight"] = (int(weight_range.group(2)), int(weight_range.group(3)))
        elif operator == "is between" and weight_range.group(3):
            filters["weight"] = (int(weight_range.group(2)), int(weight_range.group(3)))
        else:
            filters["weight"] = ("=", int(weight_range.group(2)))

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
        query &= Q(address__icontains=filters["address"])

    # Handle profession
    if filters.get("profession"):
        # Search for profession in the related TalentCategory's category_name field through SkillProfile
        query &= Q(skillprofile__talent_category__category_name__icontains=filters["profession"])

    # # Handle descriptive terms
    # if filters.get("descriptions"):
    #     for term in filters["descriptions"]:
    #         query |= (
    #                 Q(talent_description__icontains=term) |
    #                 Q(skillprofile__achievements__icontains=term) |
    #                 Q(skillprofile__talent_category__category_name__icontains=term)
    #         )

    # Now apply the query to the Talent model to fetch the matching profiles
    results = Talent.objects.filter(query)

    print("Constructed Query:", query)

    return results
