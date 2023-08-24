"""one_page_ambiguity_base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
# from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.ToLoginView.as_view(), name="login_"),
    # path('login/', auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    path("signedout/", views.SignedOutView.as_view(), name="signedout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("inputUS/", include("inputUS.urls")),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
