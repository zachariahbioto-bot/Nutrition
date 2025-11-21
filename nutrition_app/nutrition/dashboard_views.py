from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date
from .models import UserProfile, MealLog, DailyStats

@login_required
def dashboard(request):
    # Get or create user profile with default values
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create default profile
        profile = UserProfile.objects.create(
            user=request.user,
            age=25,
            gender='M',
            height_cm=170,
            weight_kg=70,
            activity_level=1.2,
            goal='maintain'
        )
    
    # Get today's date
    today = date.today()
    
    # Get or create today's stats
    daily_stats, created = DailyStats.objects.get_or_create(
        user=request.user,
        date=today,
        defaults={
            'target_calories': profile.target_calories,
            'target_protein_g': (profile.target_calories * profile.protein_ratio / 100) / 4,
            'target_carbs_g': (profile.target_calories * profile.carbs_ratio / 100) / 4,
            'target_fats_g': (profile.target_calories * profile.fats_ratio / 100) / 9,
        }
    )
    
    # Get today's meals
    today_meals = MealLog.objects.filter(user=request.user, meal_date=today)
    
    # Calculate totals
    total_calories = sum(meal.calories for meal in today_meals)
    total_protein = sum(meal.protein_g for meal in today_meals)
    total_carbs = sum(meal.carbs_g for meal in today_meals)
    total_fats = sum(meal.fats_g for meal in today_meals)
    
    # Calculate percentages
    calories_percent = (total_calories / profile.target_calories * 100) if profile.target_calories else 0
    protein_percent = (total_protein / daily_stats.target_protein_g * 100) if daily_stats.target_protein_g else 0
    carbs_percent = (total_carbs / daily_stats.target_carbs_g * 100) if daily_stats.target_carbs_g else 0
    fats_percent = (total_fats / daily_stats.target_fats_g * 100) if daily_stats.target_fats_g else 0
    
    # Remaining
    remaining_calories = profile.target_calories - total_calories
    remaining_protein = daily_stats.target_protein_g - total_protein
    remaining_carbs = daily_stats.target_carbs_g - total_carbs
    remaining_fats = daily_stats.target_fats_g - total_fats
    
    context = {
        'profile': profile,
        'today_meals': today_meals,
        'total_calories': round(total_calories, 1),
        'total_protein': round(total_protein, 1),
        'total_carbs': round(total_carbs, 1),
        'total_fats': round(total_fats, 1),
        'calories_percent': round(calories_percent, 1),
        'protein_percent': round(protein_percent, 1),
        'carbs_percent': round(carbs_percent, 1),
        'fats_percent': round(fats_percent, 1),
        'remaining_calories': round(remaining_calories, 1),
        'remaining_protein': round(remaining_protein, 1),
        'remaining_carbs': round(remaining_carbs, 1),
        'remaining_fats': round(remaining_fats, 1),
        'daily_stats': daily_stats,
    }
    
    return render(request, 'dashboard.html', context)
