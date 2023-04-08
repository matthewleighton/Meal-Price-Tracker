from django.db import models
from django.contrib.auth.models import User

from .meal_instance import MealInstance
from .standard_ingredient import StandardIngredient

from decimal import getcontext
from pint import UnitRegistry

class Meal(models.Model):
	name = models.CharField(max_length=200)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

	@property
	def meal_instances(self):
		return MealInstance.objects.filter(meal=self).order_by('-date')


	@property
	def average_price(self):
		return 20

	@property
	def standard_ingredients(self):
		return StandardIngredient.objects.filter(meal=self)

	def get_food_items(self):
		return [ingredient.food_item for ingredient in self.standard_ingredients ]
	
	def get_newest_price(self, format=True):
		if len(self.standard_ingredients) == 0:
			return 0

		ingredient_prices = [ingredient.get_newest_price(format=False) for ingredient in self.standard_ingredients]
		ingredient_prices = [price for price in ingredient_prices if price is not None]

		meal_price = sum(ingredient_prices)

		if not format:
			return meal_price
		
		meal_price = round(meal_price, 2)

		# TODO: Properly handle currency.
		currency = 'EUR'
		
		return f'{meal_price} {currency}'

	# Return the cost of the required amounts of an ingredient for the meal.
	def get_newest_ingredient_price(self, ingredient):
		if isinstance(ingredient, str):
			ingredient = StandardIngredient.objects.get(meal=self, food_item__name__iexact=ingredient)

		return ingredient.get_newest_price(format=False)

	# Return the quantity of a food item required for the meal.
	# If the food item is not used in the meal, return 0.
	def get_food_item_quantity(self, food_item):
		ingredient = StandardIngredient.objects.filter(meal=self, food_item=food_item)

		if not ingredient.exists():
			return 0
		
		quantity = ingredient[0].quantity
		unit = ingredient[0].unit

		return f'{quantity} {unit}'