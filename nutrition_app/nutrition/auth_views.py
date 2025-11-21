from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Validation
        if password != password2:
            messages.error(request, "Passwords don't match!")
            return render(request, 'auth/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'auth/signup.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('dashboard')
    
    return render(request, 'auth/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out successfully!")
    return redirect('home')


def profile_setup_view(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        activity = request.POST.get('activity')
        goal = request.POST.get('goal')
        
        # Debug: Check if values are received
        print(f"Received: age={age}, gender={gender}, height={height}, weight={weight}")
        
        # Validate all fields are present
        if not all([age, gender, height, weight, activity, goal]):
            messages.error(request, "All fields are required!")
            return render(request, 'auth/profile_setup.html')
        
        try:
            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.age = int(age)
            profile.gender = gender
            profile.height_cm = float(height)
            profile.weight_kg = float(weight)
            profile.activity_level = float(activity)
            profile.goal = goal
            profile.save()
            
            messages.success(request, "Profile setup complete!")
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'auth/profile_setup.html')
    
    return render(request, 'auth/profile_setup.html')
