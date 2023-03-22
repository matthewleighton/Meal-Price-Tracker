from datetime import date, timedelta
from decimal import Decimal
from pprint import pprint

import pytest

from meals.models import FoodItem, FoodPurchase, Meal, MealInstance, StandardIngredient

# Test that getting a meal's standard ingredients returns the correct items.
def test_get_meal_standard_ingredients(user):
	# Creating porridge
	porridge = Meal.objects.create(name='Porridge', user=user)
	oats 	 = FoodItem.objects.create(name='Oats', user=user)
	milk 	 = FoodItem.objects.create(name='Milk', user=user)
	expected_porridge_ingredients = [
		StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g'),
		StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')
	]
		
	# Creating toast
	toast = Meal.objects.create(name='Toast', user=user)
	jam   = FoodItem.objects.create(name='Jam', user=user)
	excepted_toast_ingredients = [
		StandardIngredient.objects.create(meal=toast, food_item=jam, quantity=1, unit='tbsp')
	]

	assert set(porridge.standard_ingredients) == set(expected_porridge_ingredients) # set() to ignore order
	assert len(porridge.standard_ingredients) == len(expected_porridge_ingredients)
	
	assert set(toast.standard_ingredients) == set(excepted_toast_ingredients)
	assert len(toast.standard_ingredients) == len(excepted_toast_ingredients)

# Test that getting a meal's standard ingredients still works when there are no ingredients.
def test_get_meal_standard_ingredients_empty(user):
	porridge = Meal.objects.create(name='Porridge', user=user)

	assert list(porridge.standard_ingredients) == []	

def test_get_meal_food_items(user):
	porridge = Meal.objects.create(name='Porridge', user=user)
	oats = FoodItem.objects.create(name='Oats', user=user)
	milk = FoodItem.objects.create(name='Milk', user=user)
	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g')
	StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')
	expected_porridge_food_items = [oats, milk]

	toast = Meal.objects.create(name='Toast', user=user)
	jam   = FoodItem.objects.create(name='Jam', user=user)
	StandardIngredient.objects.create(meal=toast, food_item=jam, quantity=1, unit='tbsp')
	expected_toast_food_items = [jam]

	assert set(porridge.get_food_items()) == set(expected_porridge_food_items)
	assert len(porridge.get_food_items()) == len(expected_porridge_food_items)

	assert set(toast.get_food_items()) == set(expected_toast_food_items)
	assert len(toast.get_food_items()) == len(expected_toast_food_items)

@pytest.mark.parametrize('num_porridge_instances, num_toast_instances', [
	(0, 0),
	(1, 0),
	(0, 1),
	(10, 5)
])
def test_meal_instances(user, num_porridge_instances, num_toast_instances):
	porridge = Meal.objects.create(name='Porridge', user=user)
	toast 	 = Meal.objects.create(name='Toast', user=user)

	porridge_instances = [
		MealInstance.objects.create(meal=porridge, date=date.today(), num_servings=1, rating=5, cook_time=10)
		for _ in range(num_porridge_instances)
	]

	toast_instances = [
		MealInstance.objects.create(meal=toast, date=date.today(), num_servings=1, rating=5, cook_time=5)
		for _ in range(num_toast_instances)
	]

	assert porridge_instances == list(porridge.meal_instances)
	assert toast_instances == list(toast.meal_instances)

# The newest meal price should be the unit cost of each ingredient multiplied by the quantity of that ingredient.
@pytest.mark.parametrize('oats_buy_price, oats_buy_qty, oats_ingredient_qty, milk_buy_price, milk_buy_qty, milk_ingredient_qty, expected_meal_price', [
	(1.00, 1000, 1000, 2.00, 500, 500, '3.00 EUR'),
	(0.50, 1000, 1000, 2.00, 500, 500, '2.50 EUR'),
	(1.00, 1000, 250, 2.00, 500, 500, '2.25 EUR'),
	(1.00, 50, 1000, 2.00, 500, 500, '22.00 EUR'),
	(1.00, 50, 1000, 50.00, 250, 500, '120.00 EUR'),
])
def test_newest_meal_price_correct(user, oats_buy_price, oats_buy_qty, oats_ingredient_qty, milk_buy_price, milk_buy_qty, milk_ingredient_qty, expected_meal_price):
	today = date.today()
	last_week = date.today() - timedelta(days=7)
	last_year = date.today() - timedelta(days=365)

	# Create meal and food items.
	porridge = Meal.objects.create(name='Porridge', user=user)
	oats = FoodItem.objects.create(name='Oats', user=user)
	milk = FoodItem.objects.create(name='Milk', user=user)

	# Add standard ingredients to meal.
	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=oats_ingredient_qty, unit='g')
	StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=milk_ingredient_qty, unit='ml')

	# New purchases. These newest meal price should be based on these.
	FoodPurchase.objects.create(food_item=oats, price_amount=oats_buy_price, currency='EUR', quantity=oats_buy_qty,
								   unit='g', location='Lidl', date=today)
	FoodPurchase.objects.create(food_item=milk, price_amount=milk_buy_price, currency='EUR', quantity=milk_buy_qty,
								   unit='ml', location='Lidl', date=today)

	# Old purchases. These should not effect the newest meal price.
	FoodPurchase.objects.create(food_item=oats, price_amount=1.23, currency='EUR', quantity=500,
								   unit='g', location='Lidl', date=last_year)
	FoodPurchase.objects.create(food_item=oats, price_amount=500, currency='EUR', quantity=500,
								   unit='g', location='Lidl', date=last_week)
	FoodPurchase.objects.create(food_item=milk, price_amount=800, currency='EUR', quantity=1,
								   unit='ml', location='Lidl', date=last_week)

	assert porridge.get_newest_price() == expected_meal_price

# The returned ingredient price should be the unit price, multiplied by the ingredient quantity.
@pytest.mark.parametrize('oats_ingredient_qty, oats_buy_qty, oats_buy_price, oats_ingredient_price', [
	(100, 100, 0.05, Decimal('0.05')),
	# (50, 100, 0.05, Decimal('0.025')), # TODO: Consider how many decimal places to use. Currently rounding to 2.
	(100, 50, 0.05, Decimal('0.10')),
	(100, 100, 0.05, Decimal('0.05')),
	(50, 100, 1.00, Decimal('0.50')),
])
def test_get_newest_ingredient_price_no_unit_conversion(user, oats_ingredient_qty, oats_buy_qty, oats_buy_price, oats_ingredient_price):
	oats = FoodItem.objects.create(name='Oats', user=user)
	porridge = Meal.objects.create(name='Porridge', user=user)
	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=oats_ingredient_qty, unit='g')
	FoodPurchase.objects.create(food_item=oats, price_amount=oats_buy_price, currency='EUR', quantity=oats_buy_qty,
								   unit='g', location='Lidl', date=date.today())

	assert porridge.get_newest_ingredient_price('oats') == oats_ingredient_price

