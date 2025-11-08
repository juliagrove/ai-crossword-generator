# crossword/views.py
from django.shortcuts import render
from .utils import crossword

def home(request):
    return render(request, "home.html")

def generate_crossword(request):
    if request.method == 'POST':
        category = request.POST.get('user_input')
        results=crossword(category, num_words=30)
        crossword_grid, across_clues, down_clues = results

        return render(
            request, 
            'crossword.html', 
            {
                'crossword_grid': crossword_grid,
                'across_clues': across_clues,
                'down_clues': down_clues
            }
        )
        
    return render(request, 'home.html')