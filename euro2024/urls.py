"""
URL configuration for euro2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from predictions.views import RegisterView

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),  # localhost:8000/admin/
    path('accounts/', include('django.contrib.auth.urls')), # localhost:8000/accounts/login/
    # Your predictions app
    path('', include('predictions.urls')),  # localhost:8000/
    path('register/', RegisterView.as_view(), name='register'),
]