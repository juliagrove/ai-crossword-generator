from django.urls import path
from . import views

app_name = "crossword"

urlpatterns = [
    path("", views.home, name="home"),
]

# <localhost>/crossword/
# <localhost>/crossword/testing