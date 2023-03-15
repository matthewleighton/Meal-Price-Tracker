from datetime import date
from pprint import pprint
from django import forms
from django.contrib import messages

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from dal import autocomplete

from .models import FoodItem, FoodPriceRecord, Meal, MealInstance, StandardIngredient
# from .models import UserDuplicateFoodItemError

from meals.models.food_item import UserDuplicateFoodItemError


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

	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['meal'].queryset = Meal.objects.filter(user=user)
		self.initial['date'] = date.today()
		


class FoodItemForm(forms.ModelForm):
	class Meta:
		model = FoodItem
		fields = ['food_item_name']

	def __init__(self, *args, **kwargs):
		self.user    = kwargs.pop('user', None)
		self.request = kwargs.pop('request', None) # Needed for passing messages.
		
		if self.user is None:
			raise ValueError('User must be provided to the FoodItemForm.')
		
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		food_item = super().save(commit=False)
		food_item.user = self.user

		if commit:
			try:
				food_item.save()

			# If the user already has a food item with the same name, return that food item.
			except UserDuplicateFoodItemError as e:
				
				if self.request: # We can only pass the message if the request is provided.
					messages.warning(
						self.request,
						f'Food item "{food_item.food_item_name}" already exists.'
					)

				return FoodItem.objects.filter(
					food_item_name__iexact=food_item.food_item_name,
					user=self.user
				).first()

		return food_item

		

	


class FoodPriceRecordForm(forms.ModelForm):
	new_food_item = forms.CharField(required=False, label="New Food Item")

	class Meta:
		model = FoodPriceRecord
		fields = ['food_item', 'new_food_item', 'price_amount', 'currency', 'quantity', 'unit', 'location', 'date']

		widgets = {
			'date': forms.DateInput(attrs={
				'type': 'date',
			})
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

		self.fields['food_item'].queryset = FoodItem.objects.filter(user=self.user)

		self.fields['food_item'].required = False
		self.fields['food_item'].required = False
		self.initial['date'] = date.today()

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
				user=self.user
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