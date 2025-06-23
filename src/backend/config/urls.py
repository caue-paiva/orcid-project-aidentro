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
from oauth.oauth_views import (
    oauth_authorize, oauth_callback, oauth_status, 
    get_user_identity, get_current_user_identity, 
    debug_session, health_check, simple_test,
    get_citation_metrics, get_citation_analysis, test_citation_analysis, quick_citation_test,
    search_researchers, get_researcher_papers, add_social_media_account, get_social_media_accounts
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # OAuth endpoints
    path('oauth/authorize/', oauth_authorize, name='oauth_authorize'),
    path('oauth/callback/', oauth_callback, name='oauth_callback'),
    path('oauth/status/', oauth_status, name='oauth_status'),
    # User identity endpoints
    path('api/user-identity/', get_user_identity, name='get_user_identity'),
    path('api/current-user-identity/', get_current_user_identity, name='get_current_user_identity'),
    # Citation analysis endpoints
    path('api/citation-metrics/', get_citation_metrics, name='get_citation_metrics'),
    path('api/citation-analysis/', get_citation_analysis, name='get_citation_analysis'),
    path('api/test-citation-analysis/', test_citation_analysis, name='test_citation_analysis'),
    path('api/quick-citation-test/', quick_citation_test, name='quick_citation_test'),
    # Search endpoints
    path('api/search-researchers/', search_researchers, name='search_researchers'),
    # Papers/Publications endpoints
    path('api/researcher-papers/', get_researcher_papers, name='get_researcher_papers'),
    # Social media endpoints
    path('api/add-social-media/', add_social_media_account, name='add_social_media_account'),
    path('api/get-social-media/', get_social_media_accounts, name='get_social_media_accounts'),
    # Debug endpoint
    path('api/debug-session/', debug_session, name='debug_session'),
    # Health check endpoint
    path('api/health/', health_check, name='health_check'),
    # Simple test endpoint
    path('api/simple-test/', simple_test, name='simple_test'),
]
