from django.contrib import admin

from .models.meal import Meal
from .models.food_item import FoodItem
from .models.food_price_record import FoodPriceRecord
from .models.standard_ingredient import StandardIngredient
from .models.meal_instance import MealInstance


admin.site.register(Meal)
admin.site.register(FoodItem)
admin.site.register(FoodPriceRecord)
admin.site.register(StandardIngredient)
admin.site.register(MealInstance)