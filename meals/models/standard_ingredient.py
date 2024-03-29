from django.db import models
from django.forms import ValidationError

from ..validators import MealValidators

# from ..helper import get_unit_conversion_factor

# A Meal is made up of a collection of StandardIngredients.
class StandardIngredient(models.Model):

	UNIT_CHOICES = (
		('g', 'Grams'),
		('kg', 'Kilograms'),
		('ml', 'Millilitres'),
		('l', 'Litres'),
		('tsp', 'Teaspoons'),
		('tbsp', 'Tablespoons'),
		('pc', 'Pieces'),
	)

	def __str__(self):
		if not hasattr(self, 'meal') or self.meal is None:
			meal_name = 'Unnamed Meal'
		else:
			meal_name = self.meal.name

		if not hasattr(self, 'food_item') or self.food_item is None:
			food_item_name = 'Unnamed Food Item'
		else:
			food_item_name = self.food_item.name

		return f'{meal_name}: {food_item_name}'

	meal = models.ForeignKey('meals.Meal',
							 on_delete=models.CASCADE)
	
	food_item = models.ForeignKey('meals.FoodItem',
								  on_delete=models.CASCADE)
	
	quantity = models.DecimalField('Quantity',
								   max_digits=6,
								   decimal_places=2)

	unit = models.CharField('Unit',
							max_length=20,
							# validators=[MealValidators.is_valid_unit],
							choices=UNIT_CHOICES)
	
	def clean(self, *args, **kwargs):
		super().clean()

		if not hasattr(self, 'meal') or self.meal is None:
			raise ValidationError('Meal must be provided')

		if not hasattr(self, 'food_item') or self.food_item is None:
			raise ValidationError('Food Item must be provided')

		if self.meal.user != self.food_item.user:
			raise ValidationError('Meal and Food Item must belong to the same user')
		
	def save(self, *args, **kwargs):
		self.full_clean()
		super().save()

	def format_quantity(self):
		return f'{self.quantity} {self.unit}'
	
	def get_newest_price(self, format='absolute'):
		return self.food_item.get_newest_price(format,
					 						   currency='EUR',
											   quantity=self.quantity, 
											   unit=self.unit
											   )