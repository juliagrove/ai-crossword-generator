# crossword/views.py
from django.shortcuts import render
from .utils import crossword


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
        }

        # if request came from fetch on the home page, return ONLY the partial
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "crossword/crossword_partial.html", context)

        # if user hits the url in the browser return full page
        return render(request, "crossword/crossword.html", context)

    # return the home screen at start
    return render(request, "crossword/home.html")
