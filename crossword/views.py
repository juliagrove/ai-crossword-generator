# crossword/views.py
import json

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import SavedCrossword
from .services.crossword_service import crossword_service


def home(request):
    if request.method == "POST":
        category = request.POST.get("user_input", "")
        size = request.POST.get("crossword-size", "small")
        error_message = None
        crossword_grid = []
        across_clues = []
        down_clues = []
        
        try:
            crossword_grid, across_clues, down_clues = crossword_service.generate(
                category, size=size
            )

        except Exception as e:
            error_message = str(e)

        context = {
            "crossword_grid": crossword_grid,
            "across_clues": across_clues,
            "down_clues": down_clues,
            "error_message": error_message,
            "category": category,
            "progress_grid": [],
            "from_saved": False,
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
            form.save()  # creates new user
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("crossword:home")


@login_required
@require_POST
def save_crossword(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        category = data.get("category")
        solution_grid = data.get("solution_grid")
        progress_grid = data.get("progress_grid")
        across_clues = data.get("across_clues")
        down_clues = data.get("down_clues")

        if not solution_grid:
            return JsonResponse(
                {"success": False, "error": "Missing required fields"},
                status=400,
            )

        saved = SavedCrossword.objects.create(
            user=request.user,
            category=category,
            solution_grid=solution_grid,
            progress_grid=progress_grid,
            across_clues=across_clues,
            down_clues=down_clues,
        )

        return JsonResponse({"success": True, "id": saved.id})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# List the users saved crosswords/progress
@login_required
def saved_crosswords(request):
    crosswords = SavedCrossword.objects.filter(user=request.user).order_by("updated_at")
    context = {
        "crosswords": crosswords,
    }
    return render(request, "crossword/saved_crosswords.html", context)


@login_required
def load_saved_crossword(request, pk):
    # load saved crosswords the same way new ones are loaded
    saved = get_object_or_404(SavedCrossword, pk=pk, user=request.user)

    context = {
        "crossword_grid": saved.solution_grid,
        "across_clues": saved.across_clues,
        "down_clues": saved.down_clues,
        "category": saved.category,
        "progress_grid": saved.progress_grid,
        "error_message": None,
        "from_saved": True,
    }
    return render(request, "crossword/crossword.html", context)


@login_required
def delete_saved_crossword(request, pk):
    cw = get_object_or_404(SavedCrossword, pk=pk, user=request.user)

    if request.method == "POST":
        cw.delete()
        return redirect("crossword:saved_crosswords")

    return redirect("crossword:saved_crosswords")
