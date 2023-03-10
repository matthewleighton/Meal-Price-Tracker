from pprint import pprint
import pytest
from datetime import date, timedelta

from django.contrib.auth.models import User

from meals.models import Meal, FoodItem, StandardIngredient

@pytest.fixture
def user(db, client):
	username = 'user1'
	password = 'password'

	user = User.objects.create_user(username=username, password=password)

	client.login(username=username, password=password)

	return user




# @pytest.fixture
# def oats(user):
# 	return FoodItem.objects.create(food_item_name='Oats', user=user)

# @pytest.fixture
# def milk(user):
# 	return FoodItem.objects.create(food_item_name='Milk', user=user)

# @pytest.fixture
# def jam(user):
# 	return FoodItem.objects.create(food_item_name='Jam', user=user)

# @pytest.fixture
# def porridge(user, oats, milk):
# 	porridge = Meal.objects.create(meal_name='Porridge', user=user)
# 	StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g')
# 	StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')
# 	return porridge

# @pytest.fixture
# def toast(user, jam):
# 	toast = Meal.objects.create(meal_name='Toast', user=user)
# 	StandardIngredient.objects.create(meal=toast, food_item=jam, quantity=1, unit='tbsp')
# 	return toast