from django import forms
from .models import FoodItem, FoodPriceRecord

class FoodItemForm(forms.ModelForm):

	class Meta:
		model = FoodItem
		fields = ['food_item_name']



class FoodPriceRecordForm(forms.ModelForm):
	class Meta:
		model = FoodPriceRecord
		fields = ['food_item', 'price_amount', 'quantity', 'currency', 'unit', 'location', 'date']