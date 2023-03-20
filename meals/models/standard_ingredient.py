from django.db import models

from ..validators import MealValidators

from ..helper import get_unit_conversion_factor

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
	
	def get_newest_price(self, format='absolute'):
		return self.food_item.get_newest_price(format,
					 						   currency='EUR',
											   quantity=self.quantity, 
											   unit=self.unit
											   )