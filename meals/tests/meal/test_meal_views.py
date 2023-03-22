from datetime import date, timedelta

from meals.models import FoodItem, Meal, MealInstance

def test_meals_endpoint_401_for_logged_out_user(client, user):
	assert client.get('/meals/').status_code == 401
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

def test_meal_list_view_create_meal_with_no_ingredients(client, user):
	meal_name = 'Porridge'
	client.force_login(user)
	assert Meal.objects.count() == 0

	post_data = {
		'ingredient-TOTAL_FORMS': 0,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': meal_name,
	}

	client.post('/meals/', post_data)
	
	assert Meal.objects.count() == 1
	assert Meal.objects.first().meal_name == meal_name

def test_meal_list_view_redirects_to_new_meal_page_after_creation(client, user):
	client.force_login(user)
	meal_name = 'Porridge'

	post_data = {
		'ingredient-TOTAL_FORMS': 0,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': meal_name,
	}

	response = client.post('/meals/', post_data)

	meal_id = Meal.objects.first().id

	assert response.status_code == 302
	assert response.url == f'/meals/{meal_id}/'

def test_meal_list_create_with_existing_food_items(client, user):
	oats = FoodItem.objects.create(name='Oats', user=user)
	milk = FoodItem.objects.create(name='Milk', user=user)
	
	meal_name = 'Porridge'

	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': meal_name,
		'ingredient-0-food_item': oats.id,
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-0-form_type': 'standard_ingredient',
		'ingredient-1-food_item': milk.id,
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
		'ingredient-1-form_type': 'standard_ingredient' 
	}

	client.force_login(user)

	response = client.post('/meals/', post_data)

	assert Meal.objects.count() == 1
	
	porridge = Meal.objects.first()
	assert porridge.meal_name == meal_name

	ingredients = porridge.standard_ingredients
	assert len(ingredients) == 2

	assert ingredients[0].food_item == oats
	assert ingredients[0].quantity == 100
	assert ingredients[0].unit == 'g'

	assert ingredients[1].food_item == milk
	assert ingredients[1].quantity == 200
	assert ingredients[1].unit == 'ml'

# Test that a meal can be created with new food items.
def test_meal_list_create_with_new_food_items(client, user):
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item': 'Oats', 
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-0-form_type': 'standard_ingredient',
		'ingredient-1-food_item': 'Milk',
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
		'ingredient-1-form_type': 'standard_ingredient',
	}

	client.force_login(user)

	client.post('/meals/', post_data)
	assert Meal.objects.count() == 1
	
	porridge = Meal.objects.first()
	assert porridge.meal_name == 'Porridge'

	food_items = FoodItem.objects.all()
	assert len(food_items) == 2

	# Check that the food items have been created correctly.
	oats = FoodItem.objects.get(name='Oats')
	milk = FoodItem.objects.get(name='Milk')

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
def test_meal_list_create_with_new_and_existing_food_items(client, user):
	oats = FoodItem.objects.create(name='Oats', user=user)
	
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item': oats.id, 
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-0-form_type': 'standard_ingredient',
		'ingredient-1-food_item': 'Milk',
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
		'ingredient-1-form_type': 'standard_ingredient'
	}

	client.force_login(user)

	client.post('/meals/', post_data)
	assert Meal.objects.count() == 1
	
	porridge = Meal.objects.first()
	assert porridge.meal_name == 'Porridge'

	food_items = FoodItem.objects.all()
	assert len(food_items) == 2

	# Check that milk has been created correctly.
	milk = FoodItem.objects.get(name='Milk')
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
	milk = FoodItem.objects.create(name='Milk', user=other_user)

	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item': 'Oats',
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-0-form_type': 'standard_ingredient',
		'ingredient-1-food_item': milk.id,
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
		'ingredient-1-form_type': 'standard_ingredient'
	}

	client.force_login(user)

	response = client.post('/meals/', post_data)

	assert Meal.objects.count() == 0

# Test that a meal cannot be created with an invalid food item id.
def test_meal_list_create_with_invalid_food_item_id(client, user):
	invalid_id = 123132423

	# Confirming that the food item does not exist.
	assert FoodItem.objects.filter(id=invalid_id).count() == 0
	
	post_data = {
		'ingredient-TOTAL_FORMS': 2,
		'ingredient-INITIAL_FORMS': 0,
		'meal_name': 'Porridge',
		'ingredient-0-food_item': 'Oats',
		'ingredient-0-quantity': 100,
		'ingredient-0-unit': 'g',
		'ingredient-1-food_item': invalid_id,
		'ingredient-1-quantity': 200,
		'ingredient-1-unit': 'ml',
	}

	client.force_login(user)
	client.post('/meals/', post_data)

	assert Meal.objects.count() == 0


def test_meals_item_logged_out_user_response_401(client):
	response = client.post('/meals/1/')
	
	assert response.status_code == 401

def test_meals_item_404_for_nonexistent_meal(client, user):
	client.force_login(user)
	response = client.post('/meals/124234234/')
	
	assert response.status_code == 404

def test_meals_item_response_403_for_other_users_meals(client, user, other_user):
	other_users_meal = Meal.objects.create(meal_name='Porridge', user=other_user)
	client.force_login(user)
	response = client.post(f'/meals/{other_users_meal.id}/')
	
	assert response.status_code == 403

def test_meals_item_valid(client, user):
	today = date.today()
	yesterday = today - timedelta(days=1)

	porridge = Meal.objects.create(meal_name='Porridge', user=user)
	instance_1 = MealInstance.objects.create(meal=porridge, date=today, num_servings=1, rating=5, cook_time=20)
	instance_2 = MealInstance.objects.create(meal=porridge, date=yesterday, num_servings=1, rating=5, cook_time=20)

	toast = Meal.objects.create(meal_name='Toast', user=user) # Create a meal that should not be returned.
	MealInstance.objects.create(meal=toast, date=today, num_servings=1, rating=5, cook_time=20)

	client.force_login(user)
	response = client.get(f'/meals/{porridge.id}/')

	assert response.status_code == 200
	assert response.context['meal'] == porridge
	assert len(response.context['meal_instances']) == 2
	assert set(response.context['meal_instances']) == set([instance_1, instance_2])