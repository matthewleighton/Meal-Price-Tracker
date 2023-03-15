from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..validators import MealValidators

# from . import FoodItem

from decimal import getcontext
from pint import UnitRegistry

from pprint import pprint


# This describes an instance of a FoodItem being purchased.
# We can use this to track the price of a FoodItem over time.
class FoodPriceRecord(models.Model):

	def __str__(self):
		return f'{self.food_item.food_item_name}: {self.price_amount} {self.currency} for {self.quantity} {self.unit} @ {self.location} on {self.date}'		

	food_item = models.ForeignKey('meals.FoodItem',
								  on_delete=models.CASCADE)

	price_amount = models.DecimalField('Price',
									   max_digits=5,
									   decimal_places=2)
	
	quantity = models.DecimalField('Quantity',
								   max_digits=6,
								   decimal_places=2)

	unit = models.CharField('Unit',
							max_length=20,
							validators=[MealValidators.is_valid_unit])

	location = models.CharField('Location', 
								max_length=100)

	date = models.DateField('Date')

	currency = models.CharField('Currency', 
								max_length=3, 
								validators=[MealValidators.is_valid_currency])
	
	def format_price(self):
		return f'{self.price_amount} {self.currency}'
	
	def format_quantity(self):
		return f'{self.quantity} {self.unit}'