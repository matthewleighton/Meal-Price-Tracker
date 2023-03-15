from datetime import date, timedelta
from django.forms import ValidationError

import pytest

from meals.models import FoodItem, FoodPriceRecord
from meals.models.food_item import UserDuplicateFoodItemError

class TestFoodItemModel:

	def test_food_item_get_newest_purchase(self, user):
		milk = FoodItem.objects.create(food_item_name='Milk', user=user)

		today = date.today()
		last_week = date.today() - timedelta(days=7)
		last_year = date.today() - timedelta(days=365)

		old_milk 	= FoodPriceRecord.objects.create(food_item=milk, price_amount=5.00, currency='EUR', quantity=1, unit='l', location='Aldi', date=last_year)
		new_milk 	= FoodPriceRecord.objects.create(food_item=milk, price_amount=1.00, currency='EUR', quantity=1, unit='l', location='Aldi', date=today)
		middle_milk = FoodPriceRecord.objects.create(food_item=milk, price_amount=2.00, currency='EUR', quantity=1, unit='l', location='Aldi', date=last_week)

		assert milk.get_newest_purchase() == new_milk

	# The user should not be able to create a FoodItem with the same name as an existing FoodItem belonging to the same user.
	def test_duplicate_food_item_same_user(self, user, client):
		food_item_name = 'Milk'

		FoodItem.objects.create(food_item_name=food_item_name, user=user)
		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 1

		with pytest.raises(UserDuplicateFoodItemError):
			FoodItem.objects.create(food_item_name=food_item_name, user=user)
			assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 1

	def test_duplicate_food_item_different_user(self, user, other_user, client):
		food_item_name = 'Milk'

		FoodItem.objects.create(food_item_name=food_item_name, user=other_user)
		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 1

		FoodItem.objects.create(food_item_name=food_item_name, user=user)
		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 2

	def test_food_items_must_have_names(self, user):
		with pytest.raises(ValidationError):
			FoodItem.objects.create(food_item_name='', user=user)
		
		assert FoodItem.objects.count() == 0