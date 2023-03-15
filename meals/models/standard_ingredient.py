from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..validators import MealValidators

# from . import Meal, FoodItem

from decimal import getcontext
from pint import UnitRegistry

from pprint import pprint






# A Meal is made up of a collection of StandardIngredients.
class StandardIngredient(models.Model):

	def __str__(self):
		return f'{self.meal.meal_name}: {self.food_item.food_item_name}'

	meal = models.ForeignKey('meals.Meal',
							 on_delete=models.CASCADE)
	
	food_item = models.ForeignKey('meals.FoodItem',
								  on_delete=models.CASCADE)
	
	quantity = models.DecimalField('Quantity',
								   max_digits=6,
								   decimal_places=2)

	unit = models.CharField('Unit',
							max_length=20,
							validators=[MealValidators.is_valid_unit])
	
	def format_quantity(self):
		return f'{self.quantity} {self.unit}'