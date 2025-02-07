from django.shortcuts import render,redirect,get_object_or_404
from .models import Seeker
from .forms import SeekerForm
from django.contrib.auth import authenticate, login
from .forms import LoginForm  # Your custom form, if needed
from django.http import JsonResponse
from .models import SearchHistory
from django.contrib import messages
from .models import Talent, SkillProfile, TalentCategory

import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from nltk.chunk import ne_chunk

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('maxent_ne_chunker')
nltk.download('words')



def register_view(request):
    if request.method == 'POST':
        form = SeekerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect after successful registration
    else:
        form = SeekerForm()

    return render(request, 'registration.html', {'form': form})




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
        # Capture the search query from the POST request
        search_query = request.POST.get('query', '')

        # Store the search query in the SearchHistory model
        SearchHistory.objects.create(query=search_query)

        # Optionally, store the query in the session for further use
        request.session['last_search'] = search_query

        # Process the search query (extract filters and search)
        results = process_search(search_query)

        # Return the results to the template
        return render(request, 'search.html', {'search_query': search_query, 'results': results})

    return render(request, 'search.html')



def interpret_query(query):
    # Tokenize the query
    tokens = word_tokenize(query.lower())

    # Remove stopwords (common words that don't provide much meaning in queries)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]

    # Initialize filters
    filters = {
        'age': None,
        'age_comparator': None,  # To store the comparator, e.g., 'above', 'below', 'more than', 'less than'
        'age_range': None,  # To store the range of ages (if "between" is found)
        'gender': None,
        'talent_category': None,
        'experience': None,
        'experience_comparator': None  # To store the comparator for experience ('more than', 'less than', etc.)
    }

    # Check for age-related terms
    for token in filtered_tokens:
        # Handle specific age comparisons (more than, less than, above, below)
        if token in ['above', 'more', 'below', 'less']:
            next_token_index = filtered_tokens.index(token) + 1
            if len(filtered_tokens) > next_token_index and filtered_tokens[next_token_index].isdigit():
                filters['age_comparator'] = 'more than' if token in ['above', 'more'] else 'less than'
                filters['age'] = int(filtered_tokens[next_token_index])

        # Handle "between X and Y" (age range)
        if 'between' in filtered_tokens and 'and' in filtered_tokens:
            start_index = filtered_tokens.index('between')
            if len(filtered_tokens) > start_index + 2 and filtered_tokens[start_index + 1].isdigit() and filtered_tokens[start_index + 3].isdigit():
                # Capture the age range as a tuple (start_age, end_age)
                filters['age_range'] = (int(filtered_tokens[start_index + 1]), int(filtered_tokens[start_index + 3]))

        # Check for gender-related terms (expand to 'man' and 'woman')
        if token in ['male', 'female', 'm', 'f', 'man', 'woman']:
            filters['gender'] = token

        # Check for talent categories (assuming we have a predefined list)
        talent_categories = TalentCategory.objects.values_list('category_name', flat=True)
        for category in talent_categories:
            # Match the entire category name as a phrase in the query, not just individual tokens
            if category.lower() in query.lower():  # Match the category as a whole phrase
                filters['talent_category'] = category
                break  # Once a match is found, no need to continue checking other categories

        # Check for experience (modify to handle more than, less than, above, below)
        if 'experience' in token:
            if len(filtered_tokens) > filtered_tokens.index(token) + 1 and filtered_tokens[filtered_tokens.index(token) + 1].isdigit():
                filters['experience'] = int(filtered_tokens[filtered_tokens.index(token) + 1])

            # Handle "more than", "less than", "above", and "below" for experience comparison
            if 'more' in filtered_tokens or 'above' in filtered_tokens:
                filters['experience_comparator'] = 'more than'
            elif 'less' in filtered_tokens or 'below' in filtered_tokens:
                filters['experience_comparator'] = 'less than'

    return filters



def process_search(query):
    # Interpret the query to extract filters
    filters = interpret_query(query)

    print("Filters:", filters)

    # Initialize the query set for talents
    talents = Talent.objects.all()

    # Apply filters to the talent query set based on extracted filters
    if filters['age']:
        if filters['age_comparator'] == 'more than':
            talents = talents.filter(age__gt=filters['age'])  # Greater than the specified age
        elif filters['age_comparator'] == 'less than':
            talents = talents.filter(age__lt=filters['age'])  # Less than the specified age
        elif filters['age_comparator'] is None:  # Just age without a comparator
            talents = talents.filter(age=filters['age'])  # Exact age match

    if filters['age_range']:
        talents = talents.filter(age__gte=filters['age_range'][0],
                                 age__lte=filters['age_range'][1])  # Age between range

    if filters['gender']:
        talents = talents.filter(gender=filters['gender'])

    if filters['talent_category']:
        category = TalentCategory.objects.filter(category_name=filters['talent_category']).first()
        if category:
            talents = talents.filter(skillprofile__talent_category=category)

    if filters['experience']:
        if filters['experience_comparator'] == 'more than':
            talents = talents.filter(experience__gt=filters['experience'])  # Greater than specified experience
        elif filters['experience_comparator'] == 'less than':
            talents = talents.filter(experience__lt=filters['experience'])  # Less than specified experience
        else:
            talents = talents.filter(experience__gte=filters['experience'])  # Default to greater than or equal to

    # Collect the results, including profile picture
    results = []
    if talents.exists():  # Only append results if talents match the filters
        for talent in talents:
            results.append({
                'title': f"{talent.first_name} {talent.last_name}",
                'description': talent.talent_description,
                'profile_picture': talent.profile_picture  # Include profile picture
            })

    return results
