from decimal import Decimal
from pprint import pprint
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

from meals.helper import get_unit_conversion_factor

from .meal import Meal
from .food_purchase import FoodPurchase

# This describes a FoodItem that can be used in a meal.
# A FoodItem becomes an ingredient when it is used in a meal.
class FoodItem(models.Model):
	food_item_name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.food_item_name
	
	def save(self, *args, **kwargs):
		
		# TODO: These should perhaps be moved to the clean() function.
		# But the problem is that the user is not available then, when we're
		# running form.is_valid() in the view.
		self.check_valid_name()
		self.check_for_duplicate()

		self.food_item_name = self.food_item_name.title()

		super().save(*args, **kwargs)

	def my_test(self):
		return 'Hello World'

	def check_valid_name(self):
		if not self.food_item_name:
			raise ValidationError('Food Item must have a name.')

	# Throw an exception if a FoodItem with the same name already exists for the user.
	def check_for_duplicate(self):
		existing_food_item = FoodItem.objects.filter(
			food_item_name__iexact=self.food_item_name,
			user = self.user
		).first()

		if existing_food_item and existing_food_item != self:
			raise UserDuplicateFoodItemError(f'A Food Item with the name {self.food_item_name} already exists for the user {self.user}')

	def get_newest_purchase(self):
		purchases = FoodPurchase.objects.filter(food_item=self).order_by('-date')

		if not purchases:
			return None
		
		return purchases[0]

	

	def get_newest_price(self, format='per-unit', currency=None, quantity=1, unit=None):
		newest_purchase = self.get_newest_purchase()

		if newest_purchase is None:
			if format:
				return 'N/A'
			else:
				return None
			
		purchase_price = newest_purchase.get_price_in_currency(currency)
		purchase_quantity = newest_purchase.quantity

		# If no unit is specified, use the SI unit of the newest purchase.
		if not unit:
			unit = newest_purchase.si_unit

		unit_conversion_factor = get_unit_conversion_factor(newest_purchase.unit, unit)
		unit_conversion_factor = Decimal(unit_conversion_factor)

		quantity = Decimal(quantity)

		price_per_purchase_unit = purchase_price / purchase_quantity
		price_per_output_unit = price_per_purchase_unit / unit_conversion_factor
		price_for_quantity = round(price_per_output_unit * quantity, 2)

		if not format:
			return price_for_quantity
		
		VALID_FORMAT_OPTIONS = ['per-unit', 'absolute']

		if format not in VALID_FORMAT_OPTIONS:
			raise ValueError(f'format must either be one of {VALID_FORMAT_OPTIONS} or False. Got {format}.')

		if format == 'absolute':
			return f'{price_for_quantity} {newest_purchase.currency}'
		elif format == 'per-unit':
			return f'{price_for_quantity} {newest_purchase.currency} / {unit}'


	# Return a list of all the meals that use this FoodItem.
	@property
	def meals(self):
		return Meal.objects.filter(
			models.Q(standardingredient__food_item=self)
		)
	
	@property
	def purchases(self):
		return FoodPurchase.objects.filter(food_item=self)
	
	


# Error to be triggered when a user tries to create a food item with a name that already exists.
class UserDuplicateFoodItemError(ValidationError):
	pass