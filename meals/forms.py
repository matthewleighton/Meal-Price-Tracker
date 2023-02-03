from django import forms
from .models import FoodItem, FoodPriceRecord, Meal, MealInstance


class MealForm(forms.ModelForm):
	class Meta:
		model = Meal
		fields = ['meal_name']


class MealInstanceForm(forms.ModelForm):
	class Meta:
		model = MealInstance
		fields = ['meal', 'date', 'num_servings', 'rating', 'cook_time']


class FoodItemForm(forms.ModelForm):
	class Meta:
		model = FoodItem
		fields = ['food_item_name']


class FoodPriceRecordForm(forms.ModelForm):
	class Meta:
		model = FoodPriceRecord
		fields = ['food_item', 'price_amount', 'quantity', 'currency', 'unit', 'location', 'date']