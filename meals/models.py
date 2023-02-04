from django.db import models
from django.contrib.auth.models import User

from .validators import MealValidators

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