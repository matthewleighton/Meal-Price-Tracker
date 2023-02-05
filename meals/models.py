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
		getcontext().prec = 6
		purchase = ingredient.food_item.get_newest_purchase()

		meal_unit = ingredient.unit
		meal_quantity = ingredient.quantity

		purchase_unit = purchase.unit
		purchase_quantity = purchase.quantity
		purchase_price = purchase.price_amount

		if meal_unit != purchase_unit:
			# Convert purchase units to meal units.
			ureg = UnitRegistry()
			purchase_quantity = ureg.Quantity(purchase_quantity, purchase_unit).to(meal_unit).magnitude

		return (purchase_price / purchase_quantity) * meal_quantity 

	# Return the cost of the meal, based on the most recent price records.
	def get_newest_price(self):
		return sum([
			self.get_newest_ingredient_price(ingredient) for ingredient in self.standard_ingredients
		])

		







class FoodItem(models.Model):
	food_item_name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.food_item_name

	def get_newest_purchase(self):
		return FoodPriceRecord.objects.filter(food_item=self).order_by('-date')[0]

class FoodPriceRecord(models.Model):
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

	def __str__(self):
		return f'{self.food_item.user.username} -- {self.food_item.food_item_name}: {self.price_amount}'


class StandardIngredient(models.Model):
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