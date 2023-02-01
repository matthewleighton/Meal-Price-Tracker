from django.contrib import admin
from .models import Meal, FoodItem, FoodPriceRecord

admin.site.register(Meal)
admin.site.register(FoodItem)
admin.site.register(FoodPriceRecord)