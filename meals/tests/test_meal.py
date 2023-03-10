from datetime import date, timedelta
from decimal import Decimal
from pprint import pprint

import pytest

from meals.models import FoodItem, FoodPriceRecord, Meal, MealInstance, StandardIngredient

# Test that getting a meal's standard ingredients returns the correct items.
def test_get_meal_standard_ingredients(user):
	# Creating porridge
	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	oats 	 = FoodItem.objects.create(food_item_name='Oats', user=user)
	milk 	 = FoodItem.objects.create(food_item_name='Milk', user=user)
	expected_porridge_ingredients = [
		StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g'),
		StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')
	]
		
	# Creating toast
	toast = Meal.objects.create(meal_name='Toast', user=user)
	jam   = FoodItem.objects.create(food_item_name='Jam', user=user)
	excepted_toast_ingredients = [
		StandardIngredient.objects.create(meal=toast, food_item=jam, quantity=1, unit='tbsp')
	]

	assert set(porridge.standard_ingredients) == set(expected_porridge_ingredients) # set() to ignore order
	assert len(porridge.standard_ingredients) == len(expected_porridge_ingredients)
	
	assert set(toast.standard_ingredients) == set(excepted_toast_ingredients)
	assert len(toast.standard_ingredients) == len(excepted_toast_ingredients)

# Test that getting a meal's standard ingredients still works when there are no ingredients.
def test_get_meal_standard_ingredients_empty(user):
	porridge = Meal.objects.create(meal_name='Porridge', user=user)

	assert list(porridge.standard_ingredients) == []	

def test_get_meal_food_items(user):
	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	oats = FoodItem.objects.create(food_item_name='Oats', user=user)
	milk = FoodItem.objects.create(food_item_name='Milk', user=user)
	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g')
	StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')
	expected_porridge_food_items = [oats, milk]

	toast = Meal.objects.create(meal_name='Toast', user=user)
	jam   = FoodItem.objects.create(food_item_name='Jam', user=user)
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
	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	toast 	 = Meal.objects.create(meal_name='Toast', user=user)

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
	(1.00, 1000, 1000, 2.00, 500, 500, Decimal('3.00')),
	(0.50, 1000, 1000, 2.00, 500, 500, Decimal('2.50')),
	(1.00, 1000, 250, 2.00, 500, 500, Decimal('2.25')),
	(1.00, 50, 1000, 2.00, 500, 500, Decimal('22.00')),
	(1.00, 50, 1000, 50.00, 250, 500, Decimal('120.00')),
])
def test_newest_meal_price_correct(user, oats_buy_price, oats_buy_qty, oats_ingredient_qty, milk_buy_price, milk_buy_qty, milk_ingredient_qty, expected_meal_price):
	today = date.today()
	last_week = date.today() - timedelta(days=7)
	last_year = date.today() - timedelta(days=365)

	# Create meal and food items.
	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	oats = FoodItem.objects.create(food_item_name='Oats', user=user)
	milk = FoodItem.objects.create(food_item_name='Milk', user=user)

	# Add standard ingredients to meal.
	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=oats_ingredient_qty, unit='g')
	StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=milk_ingredient_qty, unit='ml')

	# New purchases. These newest meal price should be based on these.
	FoodPriceRecord.objects.create(food_item=oats, price_amount=oats_buy_price, currency='EUR', quantity=oats_buy_qty,
								   unit='g', location='Lidl', date=today)
	FoodPriceRecord.objects.create(food_item=milk, price_amount=milk_buy_price, currency='EUR', quantity=milk_buy_qty,
								   unit='ml', location='Lidl', date=today)

	# Old purchases. These should not effect the newest meal price.
	FoodPriceRecord.objects.create(food_item=oats, price_amount=1.23, currency='EUR', quantity=500,
								   unit='g', location='Lidl', date=last_year)
	FoodPriceRecord.objects.create(food_item=oats, price_amount=500, currency='EUR', quantity=500,
								   unit='g', location='Lidl', date=last_week)
	FoodPriceRecord.objects.create(food_item=milk, price_amount=800, currency='EUR', quantity=1,
								   unit='ml', location='Lidl', date=last_week)


	assert porridge.get_newest_price() == expected_meal_price

# The returned ingredient price should be the unit price, multiplied by the ingredient quantity.
@pytest.mark.parametrize('oats_ingredient_qty, oats_buy_qty, oats_buy_price, oats_ingredient_price', [
	(100, 100, 0.05, Decimal('0.05')),
	(50, 100, 0.05, Decimal('0.025')),
	(100, 50, 0.05, Decimal('0.10')),
	(100, 100, 0.05, Decimal('0.05')),
	(50, 100, 1.00, Decimal('0.50')),
])
def test_get_newest_ingredient_price_no_unit_conversion(user, oats_ingredient_qty, oats_buy_qty, oats_buy_price, oats_ingredient_price):
	oats = FoodItem.objects.create(food_item_name='Oats', user=user)
	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=oats_ingredient_qty, unit='g')
	FoodPriceRecord.objects.create(food_item=oats, price_amount=oats_buy_price, currency='EUR', quantity=oats_buy_qty,
								   unit='g', location='Lidl', date=date.today())

	assert porridge.get_newest_ingredient_price('oats') == oats_ingredient_price


##############################################################################
#------------------------------- Testing Views ------------------------------#
##############################################################################

def test_meals_endpoint_redirect_logged_out(client, user):
	assert client.get('/meals/').status_code == 302
	client.force_login(user)
	assert client.get('/meals/').status_code == 200

# Test that the meals endpoint returns the correct meals for the logged in user.
def test_meals_endpoint_context_meals(client, user, other_user):
	Meal.objects.create(meal_name='Porridge', user=user)
	Meal.objects.create(meal_name='Toast', user=user)
	Meal.objects.create(meal_name='Pizza', user=other_user)

	client.force_login(user)
	response = client.get('/meals/')

	assert response.status_code == 200
	assert set(response.context['meals']) == set(Meal.objects.filter(user=user))
	assert len(response.context['meals']) == 2


def test_meals_new_GET_requests_return_405(client, user):
	# Loggged out
	assert client.get('/meals/new/').status_code == 405
	
	# Logged in
	client.force_login(user)
	assert client.get('/meals/new/').status_code == 405

def test_meals_new_logged_out_user_redirected_to_homepage(client, user):
	response = client.post('/meals/new/')
	
	assert response.status_code == 302
	assert response.url == '/'

def test_meals_new_logged_in_user_creates_meal_no_ingredients(client, user):
	meal_name = 'Porridge'

	client.force_login(user)
	
	assert Meal.objects.count() == 0


	post_data = {
		'ingredient-TOTAL_FORMS': 0,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': meal_name,
	}

	response = client.post('/meals/new/', post_data)
	
	assert Meal.objects.count() == 1
	assert Meal.objects.first().meal_name == meal_name
	assert response.status_code == 302


	meal_id = Meal.objects.first().id
	assert response.url == f'/meals/{meal_id}/'

	# Create a second meal.
	post_data = {
		'ingredient-TOTAL_FORMS': 0,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Toast',
	}

	response = client.post('/meals/new/', post_data)
	assert Meal.objects.count() == 2
	assert response.status_code == 302
	
	meal_id = Meal.objects.last().id
	assert response.url == f'/meals/{meal_id}/'

# Test that a meal can be created with existing food items.
def tests_meals_create_with_existing_food_items(client, user):
	# Create the existing food items
	oats = FoodItem.objects.create(food_item_name='Oats', user=user)
	milk = FoodItem.objects.create(food_item_name='Milk', user=user)
	
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item_id': oats.id,
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-1-food_item_id': milk.id,
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
	}

	client.force_login(user)

	client.post('/meals/new/', post_data)
	assert Meal.objects.count() == 1
	
	porridge = Meal.objects.first()
	assert porridge.meal_name == 'Porridge'

	ingredients = porridge.standard_ingredients
	assert len(ingredients) == 2

	assert ingredients[0].food_item == oats
	assert ingredients[0].quantity == 100
	assert ingredients[0].unit == 'g'

	assert ingredients[1].food_item == milk
	assert ingredients[1].quantity == 200
	assert ingredients[1].unit == 'ml'

# Test that a meal can be created with new food items.
def test_meals_create_with_new_food_items(client, user):
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item_id': '', 
		'ingredient-0-food_item_name': 'Oats',
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-1-food_item_id': '',
		'ingredient-1-food_item_name': 'Milk',
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
	}

	client.force_login(user)

	client.post('/meals/new/', post_data)
	assert Meal.objects.count() == 1
	
	porridge = Meal.objects.first()
	assert porridge.meal_name == 'Porridge'

	food_items = FoodItem.objects.all()
	assert len(food_items) == 2

	# Check that the food items have been created correctly.
	oats = FoodItem.objects.get(food_item_name='Oats')
	milk = FoodItem.objects.get(food_item_name='Milk')

	assert oats.user == user
	assert milk.user == user

	ingredients = porridge.standard_ingredients
	assert len(ingredients) == 2

	assert ingredients[0].food_item == oats
	assert ingredients[0].quantity == 100
	assert ingredients[0].unit == 'g'

	assert ingredients[1].food_item == milk
	assert ingredients[1].quantity == 200
	assert ingredients[1].unit == 'ml'

# Test that a meal can be created with new and existing food items.
def test_meals_create_with_new_and_existing_food_items(client, user):
	# Oats already exists before the request.
	oats = FoodItem.objects.create(food_item_name='Oats', user=user)
	
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item_id': oats.id, 
		'ingredient-0-food_item_name': '',
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-1-food_item_id': '',
		'ingredient-1-food_item_name': 'Milk',
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
	}

	client.force_login(user)

	client.post('/meals/new/', post_data)
	assert Meal.objects.count() == 1
	
	porridge = Meal.objects.first()
	assert porridge.meal_name == 'Porridge'

	food_items = FoodItem.objects.all()
	assert len(food_items) == 2

	# Check that milk has been created correctly.
	milk = FoodItem.objects.get(food_item_name='Milk')
	assert milk.user == user

	ingredients = porridge.standard_ingredients
	assert len(ingredients) == 2

	assert ingredients[0].food_item == oats
	assert ingredients[0].quantity == 100
	assert ingredients[0].unit == 'g'

	assert ingredients[1].food_item == milk
	assert ingredients[1].quantity == 200
	assert ingredients[1].unit == 'ml'

# Test that a meal cannot be created when a food_item id belongs to a different user.
def test_meals_create_with_other_users_food_item(client, user, other_user):
	milk = FoodItem.objects.create(food_item_name='Milk', user=other_user)

	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item_id': '', 
		'ingredient-0-food_item_name': 'Oats',
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-1-food_item_id': milk.id,
		'ingredient-1-food_item_name': '',
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
	}

	client.force_login(user)

	response = client.post('/meals/new/', post_data)
	assert response.status_code == 403

	assert Meal.objects.count() == 0

# Test that a meal cannot be created with an invalid food item id.
def test_meals_create_with_invalid_food_item_id(client, user):
	invalid_id = 123132423

	# Confirming that the food item does not exist.
	assert FoodItem.objects.filter(id=invalid_id).count() == 0
	
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item_id': '', 
		'ingredient-0-food_item_name': 'Oats',
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-1-food_item_id': invalid_id,
		'ingredient-1-food_item_name': '',
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
	}

	client.force_login(user)
	client.post('/meals/new/', post_data)

	assert Meal.objects.count() == 0


def test_meals_create_logged_out_user_redirected_to_homepage(client):
	response = client.post('/meals/new/')
	
	assert response.status_code == 302
	assert response.url == '/'

def test_meals_item_logged_out_user_redirected_to_homepage(client):
	response = client.post('/meals/1/')
	
	assert response.status_code == 302
	assert response.url == '/'

def test_meals_item_404_for_nonexistent_meal(client, user):
	client.force_login(user)
	response = client.post('/meals/124234234/')
	
	assert response.status_code == 404

# The user should be redirected to the homepage if they try to access a meal that is not theirs.
def test_meals_item_redirect_to_homepage_for_other_users_meals(client, user, other_user):
	other_users_meal = Meal.objects.create(meal_name='Porridge', user=other_user)
	client.force_login(user)
	response = client.post(f'/meals/{other_users_meal.id}/')
	
	assert response.status_code == 302
	assert response.url == '/'

# Test that the meals_item endpoint returns the correct meal and meal instances for the logged in user.
def test_meals_item_success(client, user):
	today = date.today()
	yesterday = today - timedelta(days=1)

	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	instance_1 = MealInstance.objects.create(meal=porridge, date=today, num_servings=1, rating=5, cook_time=20)
	instance_2 = MealInstance.objects.create(meal=porridge, date=yesterday, num_servings=1, rating=5, cook_time=20)

	toast = Meal.objects.create(meal_name='Toast', user=user) # Create a meal that should not be returned.
	MealInstance.objects.create(meal=toast, date=today, num_servings=1, rating=5, cook_time=20)

	client.force_login(user)
	response = client.post(f'/meals/{porridge.id}/')

	assert response.status_code == 200
	assert response.context['meal'] == porridge
	assert len(response.context['meal_instances']) == 2
	assert set(response.context['meal_instances']) == set([instance_1, instance_2])