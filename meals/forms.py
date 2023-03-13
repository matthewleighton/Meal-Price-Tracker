from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from dal import autocomplete

from .models import FoodItem, FoodPriceRecord, Meal, MealInstance, StandardIngredient


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

class StandardIngredientForm(forms.ModelForm):
	class Meta:
		model = StandardIngredient
		# fields = ['quantity', 'unit', 'food_item_name', 'food_item_id']
		fields = ['quantity', 'unit']

	food_item_name = forms.CharField(max_length=50, label="Food Item Name", required=False)
	food_item_id = forms.IntegerField(required=False)

	field_order = ['food_item_name', 'food_item_id', 'quantity', 'unit']


		# widgets = {
		# 	'food_item': autocomplete.ModelSelect2(
		# 		url='food_item_autocomplete',
		# 		attrs={
		# 			'data-placeholder': 'Ingredient Name',
		# 			'data-minimum-input-length': 1,
		# 			'data-trigger-dropdown': 'false'
		# 		}
		# 	)
		# }

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# self.fields['meal'].widget = forms.HiddenInput()
		# self.fields['food_item'].widget = forms.HiddenInput()

		self.helper = FormHelper()
		self.helper.layout = Layout(
			# 'meal',
			'food_item',
			'quantity',
			'unit',
			Submit('submit', 'Submit')
		)
		self.helper.form_method = 'POST'
		self.helper.form_class = 'form-horizontal'
