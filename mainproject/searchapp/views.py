from django.shortcuts import render,redirect,get_object_or_404
from .models import Seeker
from .forms import SeekerForm
from django.contrib.auth import authenticate, login
from .forms import LoginForm  # Your custom form, if needed
from django.http import JsonResponse
from django.shortcuts import render
from .models import SearchHistory
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm


def register_view(request):
    if request.method == 'POST':
        form = SeekerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register.html')
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
                    messages.success(request, 'Login successful!')
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

        # Process the search query (here, we mock the results for demonstration)
        results = process_search(search_query)

        # Return the results to the template
        return render(request, 'search.html', {'search_query': search_query, 'results': results})

    return render(request, 'search.html')


def process_search(query):
    # Example function to "process" the search query.
    # Replace with actual search logic (e.g., searching the database, performing a lookup, etc.)
    # For now, we just return mock results for the demonstration.

    mock_results = [
        {"title": "Result 1", "description": "This is a description for result 1."},
        {"title": "Result 2", "description": "This is a description for result 2."},
        {"title": "Result 3", "description": "This is a description for result 3."},
    ]

    # You could use query to filter real database models here, like:
    # results = SomeModel.objects.filter(title__icontains=query)

    return mock_results
