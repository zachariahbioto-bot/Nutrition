from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime
from .models import Food, MealLog, DailyStats, UserProfile

@login_required
def add_meal(request):
    if request.method == 'POST':
        meal_type = request.POST.get('meal_type')
        food_id = request.POST.get('food_id')
        amount_g = request.POST.get('amount')
        
        try:
            food = Food.objects.get(id=food_id)
            
            # Calculate nutrition based on amount
            # Base nutrition is per 100g, scale it
            multiplier = float(amount_g) / 100
            
            calories = food.calories * multiplier
            protein = food.protein_g * multiplier
            carbs = food.carbs_g * multiplier
            fats = food.fats_g * multiplier
            
            # Create meal log
            meal = MealLog.objects.create(
                user=request.user,
                food=food,
                meal_type=meal_type,
                amount_g=float(amount_g),
                calories=calories,
                protein_g=protein,
                carbs_g=carbs,
                fats_g=fats,
                meal_date=date.today()
            )
            
            # Update daily stats
            update_daily_stats(request.user, date.today())
            
            messages.success(request, f"Meal logged successfully!")
            return redirect('dashboard')
            
        except Food.DoesNotExist:
            messages.error(request, "Food not found!")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    # Get all foods for selection
    foods = Food.objects.all().order_by('name')
    
    # Determine meal type based on time
    current_hour = datetime.now().hour
    if 6 <= current_hour < 11:
        suggested_meal = 'breakfast'
    elif 11 <= current_hour < 15:
        suggested_meal = 'lunch'
    elif 17 <= current_hour < 21:
        suggested_meal = 'dinner'
    else:
        suggested_meal = 'snack'
    
    context = {
        'foods': foods,
        'suggested_meal': suggested_meal,
    }
    
    return render(request, 'meals/add_meal.html', context)


def update_daily_stats(user, date_obj):
    """Update or create daily stats for a user"""
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return
    
    # Get all meals for today
    meals = MealLog.objects.filter(user=user, meal_date=date_obj)
    
    # Calculate totals
    total_calories = sum(meal.calories for meal in meals)
    total_protein = sum(meal.protein_g for meal in meals)
    total_carbs = sum(meal.carbs_g for meal in meals)
    total_fats = sum(meal.fats_g for meal in meals)
    
    # Update or create daily stats
    daily_stats, created = DailyStats.objects.update_or_create(
        user=user,
        date=date_obj,
        defaults={
            'total_calories': total_calories,
            'total_protein_g': total_protein,
            'total_carbs_g': total_carbs,
            'total_fats_g': total_fats,
            'target_calories': profile.target_calories,
            'target_protein_g': (profile.target_calories * profile.protein_ratio / 100) / 4,
            'target_carbs_g': (profile.target_calories * profile.carbs_ratio / 100) / 4,
            'target_fats_g': (profile.target_calories * profile.fats_ratio / 100) / 9,
            'meals_logged': meals.count(),
        }
    )


@login_required
def delete_meal(request, meal_id):
    try:
        meal = MealLog.objects.get(id=meal_id, user=request.user)
        meal_date = meal.meal_date
        meal.delete()
        
        # Update daily stats
        update_daily_stats(request.user, meal_date)
        
        messages.success(request, "Meal deleted successfully!")
    except MealLog.DoesNotExist:
        messages.error(request, "Meal not found!")
    
    return redirect('dashboard')
