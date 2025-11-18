from django.urls import path
from . import views

app_name = "crossword"

urlpatterns = [
    path("", views.home, name="home"),
    # path("save/", views.save_crossword_progress, name="save_crossword"),
]
