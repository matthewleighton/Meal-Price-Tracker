from pprint import pprint

from meals.models.food_item import FoodItem
from meals.models.meal import Meal
from meals.models.standard_ingredient import StandardIngredient



class TestStandardIngredientViews:

	def test_logged_out_user_401_upon_ingredient_create(self, user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=user)

		response = client.post(f'/meals/{porridge.id}/', {
			'food_item': oats.id,
			'quantity': 100,
			'unit': 'g',
			'form_type': 'standard_ingredient'
		})

		assert response.status_code == 401

	def test_create_ingredient_for_other_users_meal_returns_403(self, user, other_user, client):
		porridge = Meal.objects.create(name='Porridge', user=other_user)
		oats = FoodItem.objects.create(name='Oats', user=user)

		client.force_login(user)

		response = client.post(f'/meals/{porridge.id}/', {
			'food_item': oats.id,
			'quantity': 100,
			'unit': 'g',
			'form_type': 'standard_ingredient'
		})

		assert response.status_code == 403
		assert porridge.standard_ingredients.count() == 0

	def test_create_ingredient_for_other_users_food_item_does_not_create(self, user, other_user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=other_user)

		client.force_login(user)

		response = client.post(f'/meals/{porridge.id}/', {
			'food_item': oats.id,
			'quantity': 100,
			'unit': 'g',
			'form_type': 'standard_ingredient'
		})

		form_errors = response.context['standard_ingredients_form'].errors

		assert porridge.standard_ingredients.count() == 0
		assert len(form_errors)
		assert 'food_item' in form_errors

	def test_create_new_ingredient_existing_food_item(self, user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=user)

		client.force_login(user)

		client.post(f'/meals/{porridge.id}/', {
			'food_item': oats.id,
			'quantity': 100,
			'unit': 'g',
			'form_type': 'standard_ingredient'
		})

		assert porridge.standard_ingredients.count() == 1

	def test_create_new_ingredient_new_food_item(self, user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)

		client.force_login(user)

		client.post(f'/meals/{porridge.id}/', {
			'food_item': 'Oats',
			'quantity': 100,
			'unit': 'g',
			'form_type': 'standard_ingredient'
		})

		assert porridge.standard_ingredients.count() == 1
		assert FoodItem.objects.count() == 1
		assert FoodItem.objects.first().name == 'Oats'
		assert FoodItem.objects.first().user == user


	def test_create_new_ingredient_empty_food_item(self, user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)

		client.force_login(user)

		response = client.post(f'/meals/{porridge.id}/', {
			'food_item': '',
			'quantity': 100,
			'unit': 'g',
			'form_type': 'standard_ingredient'
		})

		form_errors = response.context['standard_ingredients_form'].errors

		assert response.status_code == 200
		assert porridge.standard_ingredients.count() == 0
		
		assert len(form_errors)
		assert 'food_item' in form_errors

	#################################################################
	# Editing Ingredients
	#################################################################

	def test_edit_ingredient(self, user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=user)
		ingredient = StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=100, unit='g')
		
		client.force_login(user)

		client.post(f'/ingredients/{ingredient.id}/', {
			'food_item': oats.id,
			'quantity': 200,
			'unit': 'kg',
			'form_type': 'standard_ingredient',
			'ingredient_id': ingredient.id
		})

		assert porridge.standard_ingredients.count() == 1
		assert porridge.standard_ingredients.first().quantity == 200
		assert porridge.standard_ingredients.first().unit == 'kg'

	def test_edit_ingredient_logged_out(self, user, client):
		porridge = Meal.objects.create(name='Porridge', user=user)
		oats = FoodItem.objects.create(name='Oats', user=user)
		ingredient = StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=100, unit='g')
		
		response = client.post(f'/ingredients/{ingredient.id}/', {
			'food_item': oats.id,
			'quantity': 200,
			'unit': 'g',
			'form_type': 'standard_ingredient',
			'ingredient_id': ingredient.id
		})

		assert response.status_code == 401
		assert porridge.standard_ingredients.count() == 1
		assert porridge.standard_ingredients.first().quantity == 100

	def test_edit_ingredient_other_users_meal(self, user, other_user, client):
		porridge = Meal.objects.create(name='Porridge', user=other_user)
		oats = FoodItem.objects.create(name='Oats', user=other_user)
		ingredient = StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=100, unit='g')
		
		client.force_login(user)

		response = client.post(f'/ingredients/{ingredient.id}/', {
			'food_item': oats.id,
			'quantity': 200,
			'unit': 'g',
			'form_type': 'standard_ingredient',
			'ingredient_id': ingredient.id
		})

		assert response.status_code == 403
		assert porridge.standard_ingredients.count() == 1
		assert porridge.standard_ingredients.first().quantity == 100