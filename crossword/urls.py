# crossword/urls.py
from django.urls import path
from . import views

app_name = "crossword"

urlpatterns = [
    path("", views.home, name="home"),
    path("save/", views.save_crossword, name="save_crossword"),
    path("saved/", views.saved_crosswords, name="saved_crosswords"),
    path("saved/<int:pk>/", views.load_saved_crossword, name="load_saved_crossword"),
]
