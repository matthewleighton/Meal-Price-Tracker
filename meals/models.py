from django.db import models
from django.contrib.auth.models import User

from .validators import MealValidators

from decimal import getcontext
from pint import UnitRegistry

from pprint import pprint

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

	# def get_newest_ingredient_prices(self):
	# 	return {
	# 		ingredient: ingredient.get_newest_price() for ingredient in self.standard_ingredients
	# 	}

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

	# Return the cost of the meal, based on the most recent price records.
	def get_newest_price(self):
		return sum([
			self.get_newest_ingredient_price(ingredient) for ingredient in self.standard_ingredients
		])

	# Return the quantity of a food item required for the meal.
	# If the food item is not used in the meal, return 0.
	def get_food_item_quantity(self, food_item):
		ingredient = StandardIngredient.objects.filter(meal=self, food_item=food_item)

		if not ingredient.exists():
			return 0
		
		quantity = ingredient[0].quantity
		unit = ingredient[0].unit

		return f'{quantity} {unit}'




# This describes a FoodItem that can be used in a meal.
# A FoodItem becomes an ingredient when it is used in a meal.
class FoodItem(models.Model):
	food_item_name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.food_item_name

	def get_newest_purchase(self):
		return FoodPriceRecord.objects.filter(food_item=self).order_by('-date')[0]
	
	# Return a list of all the meals that use this FoodItem.
	@property
	def meals(self):
		return Meal.objects.filter(
			models.Q(standardingredient__food_item=self)
		)
	
	@property
	def purchases(self):
		return FoodPriceRecord.objects.filter(food_item=self)

# This describes an instance of a FoodItem being purchased.
# We can use this to track the price of a FoodItem over time.
class FoodPriceRecord(models.Model):

	def __str__(self):
		return f'{self.food_item.food_item_name}: {self.price_amount} {self.currency} for {self.quantity} {self.unit} @ {self.location} on {self.date}'		

	food_item = models.ForeignKey(FoodItem,
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

# A Meal is made up of a collection of StandardIngredients.
class StandardIngredient(models.Model):

	def __str__(self):
		return f'{self.meal.meal_name}: {self.food_item.food_item_name}'

	meal = models.ForeignKey(Meal,
							 on_delete=models.CASCADE)
	
	food_item = models.ForeignKey(FoodItem,
								  on_delete=models.CASCADE)
	
	quantity = models.DecimalField('Quantity',
								   max_digits=6,
								   decimal_places=2)

	unit = models.CharField('Unit',
							max_length=20,
							validators=[MealValidators.is_valid_unit])
	
	def format_quantity(self):
		return f'{self.quantity} {self.unit}'

# This describes a particular time when a Meal was made.
class MealInstance(models.Model):
	meal = models.ForeignKey(Meal,
							 on_delete=models.CASCADE)
	date = models.DateField('Date')
	num_servings = models.PositiveIntegerField('Number of Servings')
	rating = models.PositiveIntegerField('Rating', validators=[MealValidators.is_valid_rating])
	cook_time = models.PositiveIntegerField('Cooking Time')

	def __str__(self):
		date_string = self.date.strftime('%m/%d/%Y')
		return f'{self.meal.meal_name} on {date_string}: {self.rating}/5 stars'
	
	def list_format(self):
		date_string = self.date.strftime('%m/%d/%Y')
		return f'{date_string} | {self.rating}/5 stars | {self.cook_time} minutes cooking time'
	
	def format_cook_time(self):
		return f'{self.cook_time} minutes'
	
	def format_rating(self):
		return f'{self.rating}/5 stars'