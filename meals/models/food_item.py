from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

from .meal import Meal
from .food_price_record import FoodPriceRecord

# This describes a FoodItem that can be used in a meal.
# A FoodItem becomes an ingredient when it is used in a meal.
class FoodItem(models.Model):
	food_item_name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.food_item_name
	
	def save(self, *args, **kwargs):
		existing_food_item = FoodItem.objects.filter(
			food_item_name__iexact=self.food_item_name,
			user = self.user
		).first()

		if existing_food_item and existing_food_item != self:
			raise UserDuplicateFoodItemError(f'A Food Item with the name {self.food_item_name} already exists for the user {self.user}')

		self.food_item_name = self.food_item_name.title()

		super().save(*args, **kwargs)

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
	


# Error to be triggered when a user tries to create a food item with a name that already exists.
class UserDuplicateFoodItemError(ValidationError):
	pass