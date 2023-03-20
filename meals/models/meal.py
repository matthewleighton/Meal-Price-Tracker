from django.db import models
from django.contrib.auth.models import User

from .meal_instance import MealInstance
from .standard_ingredient import StandardIngredient

from decimal import getcontext
from pint import UnitRegistry

class Meal(models.Model):
	meal_name = models.CharField(max_length=200)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.meal_name

	@property
	def meal_instances(self):
		return MealInstance.objects.filter(meal=self)

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

		meal_price = sum(ingredient_prices)

		if not format:
			return meal_price
		
		meal_price = round(meal_price, 2)
		
		# TODO: Properly handle currency.
		return f'{meal_price} {self.standard_ingredients[0].food_item.get_newest_purchase().currency}'			

	# Return the cost of the required amounts of an ingredient for the meal.
	def get_newest_ingredient_price(self, ingredient):

		if isinstance(ingredient, str):
			ingredient = StandardIngredient.objects.get(meal=self, food_item__food_item_name__iexact=ingredient)

		getcontext().prec = 6
		purchase = ingredient.food_item.get_newest_purchase()

		meal_unit = ingredient.unit
		meal_quantity = ingredient.quantity

		purchase_unit = purchase.unit
		purchase_quantity = purchase.quantity
		purchase_price = purchase.price_amount

		if meal_unit != purchase_unit:
			# Convert purchase units to meal units.
			
			#TODO: We need to handle the case where the meal unit and purchase units cannot be converted.
			# e.g. length vs mass. Perhaps FoodItems should have a "unit type" definition.
			# Or ingredients and purchases have their unit options limited by the choise of the base FoodItem.

			ureg = UnitRegistry()
			purchase_quantity = ureg.Quantity(purchase_quantity, purchase_unit).to(meal_unit).magnitude

		return (purchase_price / purchase_quantity) * meal_quantity 

	# Return the quantity of a food item required for the meal.
	# If the food item is not used in the meal, return 0.
	def get_food_item_quantity(self, food_item):
		ingredient = StandardIngredient.objects.filter(meal=self, food_item=food_item)

		if not ingredient.exists():
			return 0
		
		quantity = ingredient[0].quantity
		unit = ingredient[0].unit

		return f'{quantity} {unit}'