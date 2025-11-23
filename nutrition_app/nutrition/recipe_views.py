from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from datetime import datetime, date
import json
import anthropic

from .models import Food, Recipe, MealLog, UserProfile

@login_required
def generate_recipe(request):
    if request.method == 'POST':
        # Get user inputs
        ingredients_text = request.POST.get('ingredients')
        meal_type = request.POST.get('meal_type')
        servings = int(request.POST.get('servings', 1))
        
        # Get user profile for calorie targets
        try:
            profile = UserProfile.objects.get(user=request.user)
            target_calories_per_meal = profile.target_calories / 3  # Rough estimate
        except UserProfile.DoesNotExist:
            target_calories_per_meal = 600
        
        try:
            # Call Claude API to generate recipes
            recipes_data = call_claude_for_recipes(
                ingredients_text, 
                meal_type, 
                servings,
                target_calories_per_meal
            )
            
            # Store in session for display
            request.session['generated_recipes'] = recipes_data
            
            return redirect('select_recipe')
            
        except Exception as e:
            messages.error(request, f"Error generating recipes: {str(e)}")
    
    # Determine suggested meal type based on time
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
        'suggested_meal': suggested_meal,
    }
    
    return render(request, 'recipes/generate.html', context)


def call_claude_for_recipes(ingredients, meal_type, servings, target_calories):
    """Call Claude API to generate recipe options"""
    
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    prompt = f"""You are a professional chef and nutritionist. Generate 3 different recipe options using the following ingredients:

Ingredients available: {ingredients}
Meal type: {meal_type}
Servings: {servings}
Target calories per serving: ~{target_calories/servings:.0f} calories

For each recipe, provide:
1. Recipe name
2. Simple step-by-step instructions
3. Estimated nutrition per serving (calories, protein, carbs, fats in grams)
4. Prep time in minutes
5. Cooking time in minutes

Return ONLY a JSON array with this exact structure (no markdown, no explanations):
[
  {{
    "name": "Recipe Name",
    "instructions": "Step 1. Do this\\nStep 2. Do that...",
    "calories": 500,
    "protein_g": 30,
    "carbs_g": 45,
    "fats_g": 15,
    "prep_time": 10,
    "cook_time": 20
  }}
]

Make recipes realistic, simple, and delicious."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse Claude's response
    response_text = message.content[0].text.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    recipes = json.loads(response_text)
    
    return recipes


@login_required
def select_recipe(request):
    recipes_data = request.session.get('generated_recipes')
    
    if not recipes_data:
        messages.error(request, "No recipes found. Please generate recipes first.")
        return redirect('generate_recipe')
    
    if request.method == 'POST':
        selected_index = int(request.POST.get('recipe_index'))
        selected_recipe = recipes_data[selected_index]
        
        # Save recipe to database
        recipe = Recipe.objects.create(
            user=request.user,
            title=selected_recipe['name'],
            meal_type=request.POST.get('meal_type', 'lunch'),
            instructions=selected_recipe['instructions'],
            ingredients_data={'source': 'ai_generated', 'raw': request.session.get('ingredients_text', '')},
            total_calories=selected_recipe['calories'],
            total_protein_g=selected_recipe['protein_g'],
            total_carbs_g=selected_recipe['carbs_g'],
            total_fats_g=selected_recipe['fats_g'],
            prep_time_minutes=selected_recipe.get('prep_time', 0) + selected_recipe.get('cook_time', 0),
            servings=1,
            is_ai_generated=True
        )
        
        # Option to log immediately
        if request.POST.get('log_now'):
            MealLog.objects.create(
                user=request.user,
                recipe=recipe,
                meal_type=recipe.meal_type,
                calories=recipe.total_calories,
                protein_g=recipe.total_protein_g,
                carbs_g=recipe.total_carbs_g,
                fats_g=recipe.total_fats_g,
                meal_date=date.today()
            )
            
            # Update daily stats
            from .meal_views import update_daily_stats
            update_daily_stats(request.user, date.today())
            
            messages.success(request, f"Recipe '{recipe.title}' created and logged!")
        else:
            messages.success(request, f"Recipe '{recipe.title}' saved!")
        
        # Clear session
        del request.session['generated_recipes']
        
        return redirect('dashboard')
    
    context = {
        'recipes': recipes_data,
    }
    
    return render(request, 'recipes/select.html', context)


@login_required
def my_recipes(request):
    recipes = Recipe.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'recipes': recipes,
    }
    
    return render(request, 'recipes/my_recipes.html', context)
