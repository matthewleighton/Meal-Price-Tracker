from datetime import date
from pprint import pprint
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User

from django_select2 import forms as s2forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from .models import FoodItem, FoodPriceRecord, Meal, MealInstance, StandardIngredient

from meals.models.food_item import UserDuplicateFoodItemError

class MealForm(forms.ModelForm):
	class Meta:
		model = Meal
		fields = ['meal_name']

	def save(self, user=None, commit=True):
		if user is None:
			raise ValueError('User must be provided to the MealForm upon save.')
		
		if not isinstance(user, User):
			raise ValueError('User provided to MealForm must be a User object.')

		meal = super().save(commit=False)
		meal.user = user

		if commit:
			meal.save()

		return meal



class MealInstanceForm(forms.ModelForm):
	class Meta:
		model = MealInstance
		fields = ['meal', 'date', 'num_servings', 'rating', 'cook_time']
		
		widgets = {
			'date': forms.DateInput(attrs={'type': 'date'})
		}

	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)

		if user is None:
			raise ValueError('User must be provided to the MealInstanceForm.')
		
		# Check the user variable is a User object.
		if not isinstance(user, User):
			raise ValueError('User must be a User object.')

		super().__init__(*args, **kwargs)

		self.fields['meal'].queryset = Meal.objects.filter(user=user)
		self.initial['date'] = date.today()
		self.fields['form_type'] = forms.CharField(widget=forms.HiddenInput, initial='meal_instance')

		


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
	

class FoodItemWidget(s2forms.ModelSelect2Widget):
	search_fields = [
		'food_item_name__icontains',
	]

class StandardIngredientForm(forms.ModelForm):
	class Meta:
		model = StandardIngredient
		fields = ['food_item', 'quantity', 'unit']

		widgets = {
			'quantity': forms.NumberInput(attrs={'required': True, 'step': '0.01', 'min': '0'}),
			'unit': forms.TextInput(attrs={'required': True}),
			'food_item': FoodItemWidget(attrs={'required': True})
		}

	field_order = ['food_item', 'quantity', 'unit']

	def __init__(self, *args, **kwargs):
		self.meal = kwargs.pop('meal', None)
		self.user = kwargs.pop('user', None)

		if self.user is None:
			raise ValueError('User must be provided to the StandardIngredientForm.')
		
		if self.meal and self.meal.user != self.user:
			raise ValueError('The meal provided to the StandardIngredientForm does not belong to the current user.')

		super().__init__(*args, **kwargs)
		self.fields['form_type'] = forms.CharField(widget=forms.HiddenInput, initial='standard_ingredient')

	def clean(self):
		cleaned_data = super().clean()


		# TODO-NEXT:
		# I think the value stored in food_item is being removed if that value is not a valid FoodItem ID.
		# This is a problem, because the field can also now be used to submit the name of a new food item.
		# So I need to prevent the clean() function from removing the value, and do the validation myself.



		# food_item_name = cleaned_data.get('food_item_name')
		# food_item_id = cleaned_data.get('food_item_id')

		# if not food_item_name and not food_item_id:
		# 	raise forms.ValidationError('Please select an existing food item or enter a new one')


		print('cleaned_data')
		pprint(cleaned_data)
		
		submitted_food_item = cleaned_data.get('food_item')

		# If a FoodItem ID was given, make sure if exists, and belongs to the current user.
		if submitted_food_item.isdigit():
			food_item_id = int(submitted_food_item)

			try:
				food_item = FoodItem.objects.get(id=food_item_id)
			except FoodItem.DoesNotExist:
				raise forms.ValidationError('The selected food item does not exist.')

			if food_item.user != self.user:
				raise forms.ValidationError('The selected food item does not belong to the current user.')


		# if food_item_id:
		# 	try:
		# 		food_item = FoodItem.objects.get(id=food_item_id)
		# 	except FoodItem.DoesNotExist:
		# 		raise forms.ValidationError('The selected food item does not exist.')

		# 	if food_item.user != self.user:
		# 		raise forms.ValidationError('The selected food item does not belong to the current user.')
		
		return cleaned_data

	def save(self, commit=True, meal=None):

		if meal: # If the meal did not exist at form creation, we can pass it in here.
			self.meal = meal

		instance = super().save(commit=False)

		food_item_id = self.cleaned_data.get('food_item_id')
		food_item_name = self.cleaned_data.get('food_item_name')

		submitted_food_item = self.cleaned_data.get('food_item')

		# If a string was submitted, check if that FoodItem already eixsts, and create it otherwise.
		if not submitted_food_item.isdigit():
			food_item_name = submitted_food_item

			try:
				food_item = FoodItem.objects.create(
					food_item_name=food_item_name,
					user=self.meal.user
				)
			except UserDuplicateFoodItemError as e:
				food_item = FoodItem.objects.filter(
					food_item_name__iexact=food_item_name,
					user=self.meal.user
				).first()
		else:
			food_item_id = int(submitted_food_item)
			food_item = FoodItem.objects.get(id=food_item_id)

		# if food_item_id:
		# 	food_item = FoodItem.objects.get(id=food_item_id)
		# 	if food_item.user != self.user:
		# 		raise forms.ValidationError('The selected food item does not belong to the current user.')
		# elif food_item_name:
		# 	try:
		# 		food_item = FoodItem.objects.create(
		# 			food_item_name=food_item_name,
		# 			user=self.meal.user
		# 		)
		# 	except UserDuplicateFoodItemError as e:
		# 		food_item = FoodItem.objects.filter(
		# 			food_item_name__iexact=food_item_name,
		# 			user=self.meal.user
		# 		).first()
		# else:
		# 	raise forms.ValidationError('Please select an existing food item or enter a new one')

		instance.food_item = food_item
		instance.meal = self.meal

		if commit:
			instance.save()

		return instance