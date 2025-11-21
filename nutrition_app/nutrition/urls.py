from django.urls import path
from . import views, auth_views, dashboard_views

urlpatterns = [
    # Landing page
    path('', views.home, name='home'),
    
    # Authentication
    path('signup/', auth_views.signup_view, name='signup'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile-setup/', auth_views.profile_setup_view, name='profile_setup'),
    
    # Dashboard
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
]
