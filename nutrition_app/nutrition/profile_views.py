from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile

@login_required
def edit_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create default profile if doesn't exist
        profile = UserProfile.objects.create(
            user=request.user,
            age=25,
            gender='M',
            height_cm=170,
            weight_kg=70,
            activity_level=1.2,
            goal='maintain'
        )
    
    if request.method == 'POST':
        try:
            # Get form data
            profile.age = int(request.POST.get('age'))
            profile.gender = request.POST.get('gender')
            profile.height_cm = float(request.POST.get('height'))
            profile.weight_kg = float(request.POST.get('weight'))
            profile.activity_level = float(request.POST.get('activity'))
            profile.goal = request.POST.get('goal')
            
            # Optional: Update macro ratios
            if request.POST.get('custom_macros'):
                profile.protein_ratio = float(request.POST.get('protein_ratio', 30))
                profile.carbs_ratio = float(request.POST.get('carbs_ratio', 40))
                profile.fats_ratio = float(request.POST.get('fats_ratio', 30))
            
            profile.save()
            
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'profile/edit_profile.html', context)


@login_required
def view_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return redirect('edit_profile')
    
    # Calculate macro targets
    target_protein_g = (profile.target_calories * profile.protein_ratio / 100) / 4
    target_carbs_g = (profile.target_calories * profile.carbs_ratio / 100) / 4
    target_fats_g = (profile.target_calories * profile.fats_ratio / 100) / 9
    
    context = {
        'profile': profile,
        'target_protein_g': round(target_protein_g, 1),
        'target_carbs_g': round(target_carbs_g, 1),
        'target_fats_g': round(target_fats_g, 1),
    }
    
    return render(request, 'profile/view_profile.html', context)
