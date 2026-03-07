from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from crossword.views import signup, logout_view, robots_txt, sitemap_xml


urlpatterns = [
    path('admin/', admin.site.urls),
    path('crossword/', include('crossword.urls')),
    path("accounts/login/", auth_views.LoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),
    path("accounts/signup/", signup, name="signup"),
    path("accounts/logout/", logout_view, name="logout"),

    path("robots.txt", robots_txt),
    path("sitemap.xml", sitemap_xml),

    # Permanent (301) redirect so search engines consolidate to /crossword/
    path("", RedirectView.as_view(url="/crossword/", permanent=True)),
]
