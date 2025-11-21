from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    """Extended user profile with nutrition data"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    ACTIVITY_CHOICES = [
        (1.2, 'Sedentary (little/no exercise)'),
        (1.375, 'Light (1-3 days/week)'),
        (1.55, 'Moderate (3-5 days/week)'),
        (1.725, 'Active (6-7 days/week)'),
        (1.9, 'Very Active (athlete)'),
    ]
    
    GOAL_CHOICES = [
        ('maintain', 'Maintain Weight'),
        ('lose', 'Lose Weight'),
        ('gain', 'Gain Weight'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Basic info
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    height_cm = models.FloatField(validators=[MinValueValidator(50)])
    weight_kg = models.FloatField(validators=[MinValueValidator(20)])
    
    # Activity & goals
    activity_level = models.FloatField(choices=ACTIVITY_CHOICES, default=1.2)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default='maintain')
    
    # Calculated fields (updated automatically)
    bmr = models.FloatField(default=0)
    tdee = models.FloatField(default=0)
    target_calories = models.FloatField(default=0)
    
    # Macro ratios (percentages)
    protein_ratio = models.FloatField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    carbs_ratio = models.FloatField(default=40, validators=[MinValueValidator(0), MaxValueValidator(100)])
    fats_ratio = models.FloatField(default=30, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_bmr(self):
        """Mifflin-St Jeor Formula"""
        if self.gender == 'M':
            bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) + 5
        else:
            bmr = (10 * self.weight_kg) + (6.25 * self.height_cm) - (5 * self.age) - 161
        return round(bmr, 2)
    
    def calculate_tdee(self):
        """Total Daily Energy Expenditure"""
        if self.bmr and self.activity_level:
            return round(self.bmr * self.activity_level, 2)
        return 0
    
    def calculate_target_calories(self):
        """Adjust calories based on goal"""
        if self.goal == 'lose':
            return round(self.tdee - 500, 2)  # 0.5kg/week loss
        elif self.goal == 'gain':
            return round(self.tdee + 300, 2)  # Lean bulk
        return self.tdee
    
    def save(self, *args, **kwargs):
        """Auto-calculate values on save"""
        if self.age and self.weight_kg and self.height_cm and self.gender:
            self.bmr = self.calculate_bmr()
            self.tdee = self.calculate_tdee()
            self.target_calories = self.calculate_target_calories()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Food(models.Model):
    """Food database with nutrition info"""
    
    name = models.CharField(max_length=200)
    serving_size = models.CharField(max_length=50, default="100g")
    
    # Macros per serving
    calories = models.FloatField(validators=[MinValueValidator(0)])
    protein_g = models.FloatField(validators=[MinValueValidator(0)])
    carbs_g = models.FloatField(validators=[MinValueValidator(0)])
    fats_g = models.FloatField(validators=[MinValueValidator(0)])
    
    # Optional micros
    fiber_g = models.FloatField(null=True, blank=True)
    sugar_g = models.FloatField(null=True, blank=True)
    sodium_mg = models.FloatField(null=True, blank=True)
    
    # Meta
    category = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.serving_size})"


class Ingredient(models.Model):
    """User's available ingredients"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount_g = models.FloatField(validators=[MinValueValidator(0)])
    added_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.food.name}: {self.amount_g}g"


class Recipe(models.Model):
    """Generated or saved recipes"""
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES)
    instructions = models.TextField()
    
    # Ingredients used (JSON)
    ingredients_data = models.JSONField()
    
    # Nutrition totals
    total_calories = models.FloatField()
    total_protein_g = models.FloatField()
    total_carbs_g = models.FloatField()
    total_fats_g = models.FloatField()
    
    # Meta
    prep_time_minutes = models.IntegerField(null=True, blank=True)
    servings = models.IntegerField(default=1)
    is_ai_generated = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class MealLog(models.Model):
    """User's logged meals"""
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPE_CHOICES)
    
    # Can log recipe OR manual food
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    amount_g = models.FloatField(null=True, blank=True)
    
    # Nutrition snapshot
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fats_g = models.FloatField()
    
    # Timestamps
    logged_at = models.DateTimeField(auto_now_add=True)
    meal_date = models.DateField()
    
    class Meta:
        ordering = ['-meal_date', '-logged_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.meal_type} on {self.meal_date}"


class DailyStats(models.Model):
    """Aggregated daily nutrition stats"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Totals
    total_calories = models.FloatField(default=0)
    total_protein_g = models.FloatField(default=0)
    total_carbs_g = models.FloatField(default=0)
    total_fats_g = models.FloatField(default=0)
    
    # Goals (snapshot from UserProfile)
    target_calories = models.FloatField()
    target_protein_g = models.FloatField()
    target_carbs_g = models.FloatField()
    target_fats_g = models.FloatField()
    
    # Meta
    meals_logged = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"