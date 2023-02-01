from django.db import models
from django.contrib.auth.models import User

from .validators import MealValidators

class Meal(models.Model):
	meal_name = models.CharField(max_length=200)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.meal_name

class FoodItem(models.Model):
	food_item_name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.food_item_name

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