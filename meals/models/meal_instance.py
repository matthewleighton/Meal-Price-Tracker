from django.db import models

from ..validators import MealValidators

# This describes a particular time when a Meal was made.
class MealInstance(models.Model):
	meal = models.ForeignKey('meals.Meal',
							 on_delete=models.CASCADE)
	date = models.DateField('Date')
	num_servings = models.PositiveIntegerField('Number of Servings')
	rating = models.PositiveIntegerField('Rating', validators=[MealValidators.is_valid_rating])
	cook_time = models.PositiveIntegerField('Cooking Time')

	def __str__(self):
		date_string = self.date.strftime('%m/%d/%Y')
		return f'{self.meal.name} on {date_string}: {self.rating}/5 stars'
	
	def list_format(self):
		date_string = self.date.strftime('%m/%d/%Y')
		return f'{date_string} | {self.rating}/5 stars | {self.cook_time} minutes cooking time'
	
	def format_cook_time(self):
		return f'{self.cook_time} minutes'
	
	def format_rating(self):
		return f'{self.rating}/5 stars'
