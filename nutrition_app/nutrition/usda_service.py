import requests
from django.conf import settings

class USDAFoodService:
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    
    def __init__(self):
        self.api_key = settings.USDA_API_KEY
    
    def search_foods(self, query, page=1, page_size=25):
        """Search for foods in USDA database"""
        url = f"{self.BASE_URL}/foods/search"
        
        params = {
            'api_key': self.api_key,
            'query': query,
            'pageSize': page_size,
            'pageNumber': page,
            'dataType': ['Survey (FNDDS)', 'Foundation', 'SR Legacy']  # Most reliable data
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse and format results
            foods = []
            for item in data.get('foods', []):
                food_data = self.parse_food_item(item)
                if food_data:
                    foods.append(food_data)
            
            return {
                'foods': foods,
                'total': data.get('totalHits', 0),
                'page': page,
                'page_size': page_size
            }
            
        except Exception as e:
            print(f"USDA API Error: {str(e)}")
            return {'foods': [], 'total': 0, 'page': 1, 'page_size': page_size}
    
    def parse_food_item(self, item):
        """Parse USDA food item into our format"""
        try:
            # Get nutrients
            nutrients = {n['nutrientName']: n.get('value', 0) 
                        for n in item.get('foodNutrients', [])}
            
            # Extract key nutrients (per 100g)
            calories = nutrients.get('Energy', 0)
            protein = nutrients.get('Protein', 0)
            carbs = nutrients.get('Carbohydrate, by difference', 0)
            fats = nutrients.get('Total lipid (fat)', 0)
            fiber = nutrients.get('Fiber, total dietary', 0)
            sugar = nutrients.get('Sugars, total including NLEA', 0)
            sodium = nutrients.get('Sodium, Na', 0)
            
            return {
                'usda_id': item.get('fdcId'),
                'name': item.get('description', ''),
                'brand': item.get('brandOwner', ''),
                'category': item.get('foodCategory', ''),
                'calories': round(calories, 1),
                'protein_g': round(protein, 1),
                'carbs_g': round(carbs, 1),
                'fats_g': round(fats, 1),
                'fiber_g': round(fiber, 1) if fiber else None,
                'sugar_g': round(sugar, 1) if sugar else None,
                'sodium_mg': round(sodium, 1) if sodium else None,
                'serving_size': '100g'
            }
        except Exception as e:
            print(f"Parse error: {str(e)}")
            return None
    
    def get_food_details(self, fdc_id):
        """Get detailed info for a specific food"""
        url = f"{self.BASE_URL}/food/{fdc_id}"
        
        params = {'api_key': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"USDA API Error: {str(e)}")
            return None
