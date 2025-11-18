# crossword/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .services.crossword_service import crossword
from django.contrib.auth import logout
import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import SavedCrossword

def home(request):
    if request.method == "POST":
        category = request.POST.get("user_input", "")
        error_message = None
        crossword_grid = []
        across_clues = []
        down_clues = []

        try:
            crossword_grid, across_clues, down_clues = crossword(category, num_words=20)

        except Exception as e:
            error_message = str(e)

        context = {
            "crossword_grid": crossword_grid,
            "across_clues": across_clues,
            "down_clues": down_clues,
            "error_message": error_message,
            "category": category
        }

        # if request came from fetch on the home page, return ONLY the partial
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "crossword/crossword_partial.html", context)

        # if user hits the url in the browser return full page
        return render(request, "crossword/crossword.html", context)

    # return the home screen at start
    return render(request, "crossword/home.html")


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # creates new user
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    """
    Log the user out and redirect to the home page
    """
    logout(request)
    return redirect("crossword:home") 


@login_required
@require_POST
def save_crossword_progress(request):
    """
    Save current crossword grid for this user+category.
    Called ONLY when the user clicks the 'Save Crossword' button.
    """
    data = json.loads(request.body)

    category = data.get("category")
    grid_state = data.get("grid_state")

    obj, created = SavedCrossword.objects.update_or_create(
        user=request.user,
        category=category,
        defaults={"grid_state": grid_state},
    )
    return JsonResponse({"status": "ok", "saved_id": obj.id, "created": created})