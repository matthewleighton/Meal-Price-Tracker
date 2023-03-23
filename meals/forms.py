from datetime import date
from pprint import pprint
from django import forms
from django.contrib import messages
from django.contrib.auth.models import User

from django_select2 import forms as s2forms

from .models import FoodItem, FoodPurchase, Meal, MealInstance, StandardIngredient

from meals.models.food_item import UserDuplicateFoodItemError

class MealForm(forms.ModelForm):
	class Meta:
		model = Meal
		fields = ['name']

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
		fields = ['name']

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
						f'Food item "{food_item.name}" already exists.'
					)

				return FoodItem.objects.filter(
					name__iexact=food_item.name,
					user=self.user
				).first()

		return food_item

		

	


class FoodPurchaseForm(forms.ModelForm):
	class Meta:
		model = FoodPurchase
		fields = ['food_item', 'price_amount', 'currency', 'quantity', 'unit', 'location', 'date']


		widgets = {
			'date': forms.DateInput(attrs={
				'type': 'date',
			})
		}

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

		self.initial['date'] = date.today()
		self.fields['food_item'] = FoodItemField(user=self.user, required=True)


class FoodItemWidget(s2forms.ModelSelect2Widget):
	search_fields = [
		'name__icontains',
	]

	def get_queryset(self):
		user = self.attrs.get('user', None)
		if user:
			return FoodItem.objects.filter(user=user)
		else:
			return FoodItem.objects.none()

class FoodItemField(forms.ModelChoiceField):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(FoodItem.objects.filter(user=self.user), *args, **kwargs)

		self.widget = FoodItemWidget(attrs={
			'data-placeholder': 'Select a food item...',
			'data-tags': 'true',
			'data-width': '500px',
			'required': True,
			'user': self.user,
		})

	def to_python(self, value):
		if value.isdigit():
			return super().to_python(value)
		
		# food_item_name = value.strip().capitalize()
		
		# existing_food_item = FoodItem.objects.filter(
		# 	name__iexact=food_item_name,
		# 	user=self.user
		# )

		# if existing_food_item:
		# 	return existing_food_item.first()


		# new_food_item = FoodItem(
		# 	name=food_item_name,
		# 	user=self.user
		# )

		# new_food_item.save()

		# return new_food_item


		# TODO: A potential problem here is that this creates and saves the new food item even if the form is not valid.
		# This means we could end up with a bunch of food items that are not used anywhere.
		# I've tried simply returning the new food item without saving it (see commented out code above),
		# but then the validation failed because the food_item fields is apparently empty.
		# Need to investigate this further.
		food_item_name = value.strip().capitalize()
		food_item, created = FoodItem.objects.get_or_create(
			user=self.user,
			name=food_item_name
		)
		return food_item
		
	def validate(self, value):
		super().validate(value)

		if value.user != self.user:
			raise forms.ValidationError('Food item does not belong to this user.')
		

class StandardIngredientForm(forms.ModelForm):
	class Meta:
		model = StandardIngredient
		fields = ['food_item', 'quantity', 'unit']

		widgets = {
			'quantity': forms.NumberInput(attrs={'required': True, 'step': '0.01', 'min': '0'}),
			'unit': forms.TextInput(attrs={'required': True}),
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
		self.fields['food_item'] = FoodItemField(user=self.user)

		if self.instance and hasattr(self.instance, 'meal'):
			self.meal = self.instance.meal

		self.instance.meal = self.meal

		self.assign_food_item()

	def save(self, commit=True, meal=None):
		if meal: # If the meal did not exist at form creation, we can pass it in here.
			self.meal = meal

		if not hasattr(self, 'meal'):
			raise ValueError('The meal must be provided to the StandardIngredientForm before saving.')

		if not isinstance(self.meal, Meal):
			raise ValueError('The meal provided to the StandardIngredientForm must be an instance of Meal.')

		if not self.instance:
			instance = super().save(commit=False)
		else:
			instance = self.instance

		instance.meal = self.meal

		if commit:
			instance.save()

		return instance
	
	def assign_food_item(self):
		food_item = self.data.get('food_item', None)

		if food_item is None:
			return
		
		if food_item == '':
			self.add_error('food_item', 'This field is required.')
			return

		if isinstance(food_item, FoodItem):
			self.instance.food_item = food_item
		elif food_item.isdigit():
			self.instance.food_item = FoodItem.objects.get(id=food_item)
		else:
			food_item_name = food_item.strip().capitalize()
			self.instance.food_item = FoodItem.objects.get_or_create(
				user=self.user,
				name=food_item_name
			)[0]

		