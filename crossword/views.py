# crossword/views.py
from django.shortcuts import render
from .utils import crossword, get_crossword_content

def home(request):
    return render(request, "home.html")

def generate_crossword(request):
    category = request.POST.get("user_input", "")
    error_message = None
    crossword_grid = []
    across_clues = []
    down_clues = []
    
    try:
        crossword_grid, across_clues, down_clues = crossword(category, num_words=30)
    
    except Exception as e:
        error_message = str(e)

    return render(
        request, 
        'crossword.html', 
        {
            'crossword_grid': crossword_grid,
            'across_clues': across_clues,
            'down_clues': down_clues,
            'error_message': error_message
        }
    )