# crossword/views.py
import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
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
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
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

        saved_crossword_id = data.get("saved_crossword_id")
        if saved_crossword_id:
            saved = get_object_or_404(SavedCrossword, pk=saved_crossword_id, user=request.user)
            saved.progress_grid = progress_grid
            saved.save()
        else:
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
    sort = request.GET.get("sort", "newest")
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "az": "category",
        "za": "-category",
    }
    order = sort_options.get(sort, "-created_at")
    crosswords = SavedCrossword.objects.filter(user=request.user).order_by(order)
    context = {
        "crosswords": crosswords,
        "current_sort": sort,
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
        "saved_id": saved.pk,
    }
    return render(request, "crossword/crossword.html", context)


@login_required
def delete_saved_crossword(request, pk):
    cw = get_object_or_404(SavedCrossword, pk=pk, user=request.user)

    if request.method == "POST":
        cw.delete()
        return redirect("crossword:saved_crosswords")

    return redirect("crossword:saved_crosswords")


def robots_txt(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    content = (
        "User-agent: *\n"
        "Allow: /crossword/\n"
        "Disallow: /crossword/saved/\n"
        "Disallow: /crossword/save/\n"
        "Disallow: /admin/\n"
        "Disallow: /accounts/\n"
        f"\nSitemap: {base_url}/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    base_url = f"{request.scheme}://{request.get_host()}"
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/crossword/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    return HttpResponse(content, content_type="application/xml")
