"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from oauth.oauth_views import oauth_authorize, oauth_callback, oauth_status, get_user_identity, get_current_user_identity

urlpatterns = [
    path('admin/', admin.site.urls),
    # OAuth endpoints
    path('oauth/authorize/', oauth_authorize, name='oauth_authorize'),
    path('oauth/callback/', oauth_callback, name='oauth_callback'),
    path('oauth/status/', oauth_status, name='oauth_status'),
    # User identity endpoints
    path('api/user-identity/', get_user_identity, name='get_user_identity'),
    path('api/current-user-identity/', get_current_user_identity, name='get_current_user_identity'),
]
