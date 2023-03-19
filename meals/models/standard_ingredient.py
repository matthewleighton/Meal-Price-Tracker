from django.db import models

from ..validators import MealValidators

from ..helper import get_conversion_factor

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
	
	def get_newest_price(self, format=True):
		newest_purchase = self.food_item.get_newest_purchase()

		if newest_purchase is None:

			if format:
				return 'N/A'
			else:
				return None

		conversion_factor = get_conversion_factor(newest_purchase.unit, self.unit)

		price_for_quantity = newest_purchase.price_amount * (self.quantity / newest_purchase.quantity)
		price_for_quantity /= conversion_factor

		return price_for_quantity if not format else f'{price_for_quantity} {newest_purchase.currency}'
