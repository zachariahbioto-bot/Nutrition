from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Food
from .usda_service import USDAFoodService
from .image_service import FoodImageService

@login_required
def search_foods(request):
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    
    results = {'foods': [], 'total': 0}
    
    if query:
        # Search USDA database
        usda_service = USDAFoodService()
        results = usda_service.search_foods(query, page=page, page_size=20)
    
    # Also search local database
    local_foods = Food.objects.filter(name__icontains=query)[:10] if query else []
    
    context = {
        'query': query,
        'usda_results': results,
        'local_foods': local_foods,
    }
    
    return render(request, 'foods/search.html', context)


@login_required
def add_food_from_usda(request):
    """Add a food from USDA database to our local database"""
    if request.method == 'POST':
        food_data = {
            'name': request.POST.get('name'),
            'calories': float(request.POST.get('calories', 0)),
            'protein_g': float(request.POST.get('protein_g', 0)),
            'carbs_g': float(request.POST.get('carbs_g', 0)),
            'fats_g': float(request.POST.get('fats_g', 0)),
            'fiber_g': float(request.POST.get('fiber_g') or 0) or None,
            'sugar_g': float(request.POST.get('sugar_g') or 0) or None,
            'sodium_mg': float(request.POST.get('sodium_mg') or 0) or None,
            'category': request.POST.get('category', ''),
            'serving_size': '100g',
            'is_verified': True
        }
        
        # Check if food already exists
        existing = Food.objects.filter(name__iexact=food_data['name']).first()
        
        if existing:
            messages.info(request, f"Food '{food_data['name']}' already exists in database")
            return redirect('search_foods')
        
        # Get image from Unsplash
        image_service = FoodImageService()
        food_data['image_url'] = image_service.get_food_image(food_data['name'])
        
        # Create new food
        food = Food.objects.create(**food_data)
        messages.success(request, f"Added '{food.name}' to database with image!")
        
        return redirect('add_meal')
    
    return redirect('search_foods')


@login_required
def add_custom_food(request):
    """Allow users to add their own custom foods"""
    if request.method == 'POST':
        try:
            food = Food.objects.create(
                name=request.POST.get('name'),
                calories=float(request.POST.get('calories')),
                protein_g=float(request.POST.get('protein_g')),
                carbs_g=float(request.POST.get('carbs_g')),
                fats_g=float(request.POST.get('fats_g')),
                serving_size=request.POST.get('serving_size', '100g'),
                category=request.POST.get('category', 'Custom'),
                is_verified=False  # User-created foods aren't verified
            )
            messages.success(request, f"Custom food '{food.name}' created!")
            return redirect('add_meal')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return render(request, 'foods/add_custom.html')
