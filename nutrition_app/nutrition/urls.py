from django.urls import path
from . import views, auth_views, dashboard_views, meal_views, profile_views, recipe_views, food_views

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
    
    # Meals
    path('meals/add/', meal_views.add_meal, name='add_meal'),
    path('meals/delete/<int:meal_id>/', meal_views.delete_meal, name='delete_meal'),
    
    # Profile
    path('profile/edit/', profile_views.edit_profile, name='edit_profile'),
    path('profile/', profile_views.view_profile, name='view_profile'),
    
    # AI Recipe Generator
    path('recipes/generate/', recipe_views.generate_recipe, name='generate_recipe'),
    path('recipes/select/', recipe_views.select_recipe, name='select_recipe'),
    path('recipes/my-recipes/', recipe_views.my_recipes, name='my_recipes'),
    
    # Food Search
    path('foods/search/', food_views.search_foods, name='search_foods'),
    path('foods/add-from-usda/', food_views.add_food_from_usda, name='add_food_from_usda'),
    path('foods/add-custom/', food_views.add_custom_food, name='add_custom_food'),
]
