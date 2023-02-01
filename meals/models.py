from django.db import models
from django.contrib.auth.models import User

class Meal(models.Model):
	meal_name = models.CharField(max_length=200)
	user = models.ForeignKey(User, on_delete=models.CASCADE)

	def __str__(self):
		return self.meal_name

class FoodItem(models.Model):
	food_item_name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)