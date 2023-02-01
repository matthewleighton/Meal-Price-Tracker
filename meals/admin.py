from django.contrib import admin
from .models import Meal, FoodItem, FoodPriceRecord, StandardIngredient

admin.site.register(Meal)
admin.site.register(FoodItem)
admin.site.register(FoodPriceRecord)
admin.site.register(StandardIngredient)