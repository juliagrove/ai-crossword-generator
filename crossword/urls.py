from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# create paths to connect URL patterns to a view

urlpatterns = [
    # URL path, function from views file, path name
    path('', views.home, name='home'),  # empty path takes you to the base url
    path('generate-crossword/', views.generate_crossword, name='generate_crossword'),
]

urlpatterns += staticfiles_urlpatterns()

# <localhost>/crossword/
# <localhost>/crossword/testing