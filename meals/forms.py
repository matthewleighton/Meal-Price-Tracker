from pprint import pprint
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
		
		widgets = {
			'date': forms.DateInput(attrs={'type': 'date'})
		}


class FoodItemForm(forms.ModelForm):
	class Meta:
		model = FoodItem
		fields = ['food_item_name']


class FoodPriceRecordForm(forms.ModelForm):
	new_food_item = forms.CharField(required=False, label="New Food Item")

	class Meta:
		model = FoodPriceRecord
		fields = ['food_item', 'new_food_item', 'price_amount', 'currency', 'quantity', 'unit', 'location', 'date']

		widgets = {
			'date': forms.DateInput(attrs={'type': 'date'})
		}

	# We add a request object to the form so that we can access the user when we save the form.
	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request', None)

		super().__init__(*args, **kwargs)
		self.fields['food_item'].required = False
		self.fields['food_item'].required = False

	# We add a validation check to ensure that either an existing food item or a new food item is given.
	def clean(self):
		cleaned_data = super().clean()
		food_item = cleaned_data.get('food_item')
		new_food_item = cleaned_data.get('new_food_item')

		if not food_item and not new_food_item:
			raise forms.ValidationError('Please select an existing food item or enter a new one')

		return cleaned_data

	# If a new food item is given, we create a new FoodItem object and save it.	
	def save(self, commit=True):
		instance = super().save(commit=False)

		food_item = self.cleaned_data.get('food_item')
		new_food_item = self.cleaned_data.get('new_food_item')

		if not food_item and new_food_item:
			food_item = FoodItem.objects.create(
				food_item_name=new_food_item,
				user=self.request.user
			)

		instance.food_item = food_item

		if commit:
			instance.save()

		return instance

class StandardIngredientForm(forms.ModelForm):
	class Meta:
		model = StandardIngredient
		fields = ['quantity', 'unit']

	food_item_name = forms.CharField(max_length=50, label="Food Item Name", required=False)
	food_item_id = forms.IntegerField(required=False)

	field_order = ['food_item_name', 'food_item_id', 'quantity', 'unit']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.layout = Layout(
			'food_item',
			'quantity',
			'unit',
			Submit('submit', 'Submit')
		)
		self.helper.form_method = 'POST'
		self.helper.form_class = 'form-horizontal'

	def clean(self):
		cleaned_data = super().clean()

		food_item_name = cleaned_data.get('food_item_name')
		food_item_id = cleaned_data.get('food_item_id')

		if not food_item_name and not food_item_id:
			raise forms.ValidationError('Please select an existing food item or enter a new one')
		
		return cleaned_data

	def save(self, meal, user, commit=True):
		instance = super().save(commit=False)

		food_item_id = self.cleaned_data.get('food_item_id')
		food_item_name = self.cleaned_data.get('food_item_name')

		if food_item_id:
			food_item = FoodItem.objects.get(id=food_item_id)
		elif food_item_name:
			food_item = FoodItem.objects.create(
				food_item_name=food_item_name,
				user=user
			)
		else:
			raise forms.ValidationError('Please select an existing food item or enter a new one')

		instance.food_item = food_item
		instance.meal = meal

		if commit:
			instance.save()

		return instance