import requests
from django.conf import settings
from django.core.cache import cache

class FoodImageService:
    """Service to fetch food images from Unsplash"""
    
    BASE_URL = "https://api.unsplash.com"
    
    def __init__(self):
        self.access_key = settings.UNSPLASH_ACCESS_KEY
    
    def get_food_image(self, food_name):
        """Get image URL for a food item"""
        # Check cache first (avoid repeated API calls)
        cache_key = f"food_image_{food_name.lower().replace(' ', '_')}"
        cached_image = cache.get(cache_key)
        
        if cached_image:
            return cached_image
        
        try:
            url = f"{self.BASE_URL}/search/photos"
            params = {
                'query': f"{food_name} food",
                'per_page': 1,
                'orientation': 'landscape',
                'client_id': self.access_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                image_url = data['results'][0]['urls']['small']
                # Cache for 7 days
                cache.set(cache_key, image_url, 60 * 60 * 24 * 7)
                return image_url
            
            # Return placeholder if no image found
            return self.get_placeholder_image()
            
        except Exception as e:
            print(f"Unsplash API Error: {str(e)}")
            return self.get_placeholder_image()
    
    def get_placeholder_image(self):
        """Return a placeholder image URL"""
        return "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400"
