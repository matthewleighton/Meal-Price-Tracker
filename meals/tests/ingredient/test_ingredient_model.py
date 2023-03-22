from pprint import pprint
from django.forms import ValidationError

import pytest

from meals.models.food_item import FoodItem
from meals.models.meal import Meal
from meals.models.standard_ingredient import StandardIngredient

class TestStandardIngredientModel:
    
	def test_create_valid_ingredient(self, user):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=user)

		ingredient = StandardIngredient.objects.create(
			meal=porridge,
			food_item=oats,
			quantity=100,
			unit='g'
		)

		assert ingredient.meal == porridge
		assert ingredient.food_item == oats
		assert ingredient.quantity == 100
		assert ingredient.unit == 'g'

	# We should not be able to create an ingredient where meal and food_item belong to different users.
	def test_different_user_for_ingredient_meal_and_food_item(self, user, other_user):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=other_user)

		with pytest.raises(ValidationError):
			StandardIngredient.objects.create(
				meal=porridge,
				food_item=oats,
				quantity=100,
				unit='g'
			)

		assert StandardIngredient.objects.count() == 0