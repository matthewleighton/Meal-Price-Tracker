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


	# By default, get_newest_price should return the price per SI unit
	@pytest.mark.parametrize('purchase_price, purchase_quantity, unit, expected_price', [
		(1.00, 1, 'l', '1.00 EUR / l'),
		(1.00, 1, 'kg', '1.00 EUR / kg'),
		(1.00, 1, 'g', '1000.00 EUR / kg'),
		(2.00, 200, 'g', '10.00 EUR / kg'),
		(1.00, 1, 'ml', '1000.00 EUR / l'),
		(1.00, 2, 'kg', '0.50 EUR / kg'),
	])
	def test_get_newest_price_defaults_to_price_per_SI(self, user, purchase_price, purchase_quantity, unit, expected_price):
		food_item = FoodItem.objects.create(food_item_name='Delicious Food Item', user=user)

		new_purchase = FoodPriceRecord.objects.create(food_item=food_item, price_amount=purchase_price, currency='EUR', quantity=purchase_quantity, unit=unit, location='Aldi', date=date.today())
		old_purchase = FoodPriceRecord.objects.create(food_item=food_item, price_amount=2.00, currency='EUR', quantity=1, unit=unit, location='Aldi', date=date.today() - timedelta(days=7))

		assert food_item.get_newest_price() == expected_price

	# If the specified format is "absolute", the price per SI unit should be returned.
	@pytest.mark.parametrize('purchase_price, purchase_quantity, unit, expected_price', [
		(1.00, 1, 'l', '1.00 EUR'),
		(1.00, 2, 'l', '0.50 EUR'),
		(1.00, 1, 'kg', '1.00 EUR'),
		(1.00, 1, 'g', '1000.00 EUR'),
		(0.01, 1, 'g', '10.00 EUR'),
		(1.00, 1, 'ml', '1000.00 EUR'),
		(0.01, 1, 'ml', '10.00 EUR'),
	])
	def test_get_newest_price_format_absolute_SI(self, user, purchase_price, purchase_quantity, unit, expected_price):
		food_item = FoodItem.objects.create(food_item_name='Delicious Food Item', user=user)
		FoodPriceRecord.objects.create(food_item=food_item, price_amount=purchase_price, currency='EUR', quantity=purchase_quantity, unit=unit, location='Aldi', date=date.today())
		
		assert food_item.get_newest_price(format='absolute') == expected_price

	@pytest.mark.parametrize('purchase_price, purchase_quantity, output_quantity, purchase_unit, expected_price', [
		(1.00, 1, 1, 'l', '1.00 EUR'),
		(1.00, 1, 2, 'l', '2.00 EUR'),
		(1.00, 1, 0.5, 'l', '0.50 EUR'),
		(1.00, 250, 4, 'g', '16.00 EUR'),
	])
	def test_get_newest_price_format_absolute_SI_quantity(self, user, purchase_price, purchase_quantity, output_quantity, purchase_unit, expected_price):
		food_item = FoodItem.objects.create(food_item_name='Delicious Food Item', user=user)
		FoodPriceRecord.objects.create(food_item=food_item, price_amount=purchase_price, currency='EUR', quantity=purchase_quantity, unit=purchase_unit, location='Aldi', date=date.today())
		
		assert food_item.get_newest_price(format='absolute', quantity=output_quantity) == expected_price

	@pytest.mark.parametrize('purchase_price, purchase_quantity, purchase_unit, output_unit, expected_price', [
		(1.00, 1, 'g', 'g', '1.00 EUR'),
		(1.00, 1, 'g', 'kg', '1000.00 EUR'),
		(100.00, 1, 'kg', 'g', '0.10 EUR'),
	])
	def test_get_newest_price_format_absolute_SI_unit(self, user, purchase_price, purchase_quantity, purchase_unit, output_unit, expected_price):
		food_item = FoodItem.objects.create(food_item_name='Delicious Food Item', user=user)
		FoodPriceRecord.objects.create(food_item=food_item, price_amount=purchase_price, currency='EUR', quantity=purchase_quantity, unit=purchase_unit, location='Aldi', date=date.today())
		
		assert food_item.get_newest_price(format='absolute', unit=output_unit) == expected_price

	@pytest.mark.parametrize('purchase_price, purchase_quantity, purchase_unit, output_quantity, output_unit, expected_price', [
		(1.00, 1, 'kg', 1, 'kg', '1.00 EUR'),
		(1.00, 1, 'kg', 2, 'kg', '2.00 EUR'),
		(1.00, 1, 'kg', 0.5, 'kg', '0.50 EUR'),
		(1.00, 1, 'g', 1, 'kg', '1000.00 EUR'),
		(1.00, 1, 'g', 1, 'g', '1.00 EUR'),
		(2.50, 2, 'kg', 1, 'kg', '1.25 EUR'),
		(2.50, 2, 'kg', 2000, 'g', '2.50 EUR'),
		(1, 0.5, 'kg', 1500, 'g', '3.00 EUR'),
	])
	def test_get_newest_price_format_absolute_SI_unit_quantity(self, user, purchase_price, purchase_quantity, purchase_unit, output_quantity, output_unit, expected_price):
		food_item = FoodItem.objects.create(food_item_name='Delicious Food Item', user=user)
		FoodPriceRecord.objects.create(food_item=food_item, price_amount=purchase_price, currency='EUR', quantity=purchase_quantity, unit=purchase_unit, location='Aldi', date=date.today())
		
		assert food_item.get_newest_price(format='absolute', unit=output_unit, quantity=output_quantity) == expected_price