from django.contrib import admin
from .models import UserProfile, Food, Ingredient, Recipe, MealLog, DailyStats
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'weight_kg', 'bmr', 'tdee', 'target_calories']
    list_filter = ['gender', 'goal', 'activity_level']
    search_fields = ['user__username']

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'serving_size', 'calories', 'protein_g', 'carbs_g', 'fats_g', 'category']
    list_filter = ['category', 'is_verified']
    search_fields = ['name']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['user', 'food', 'amount_g', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'food__name']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'meal_type', 'total_calories', 'servings', 'is_ai_generated', 'created_at']
    list_filter = ['meal_type', 'is_ai_generated']
    search_fields = ['title', 'user__username']

@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'meal_type', 'meal_date', 'calories', 'protein_g', 'carbs_g', 'fats_g']
    list_filter = ['meal_type', 'meal_date']
    search_fields = ['user__username']
    date_hierarchy = 'meal_date'

@admin.register(DailyStats)
class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_calories', 'target_calories', 'meals_logged']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'