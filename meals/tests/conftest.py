from pprint import pprint
import pytest
from datetime import date, timedelta

from django.contrib.auth.models import User

from meals.models import Meal, FoodItem, StandardIngredient

@pytest.fixture
def user(db, client):
	username = 'user1'
	password = 'password'

	return User.objects.create_user(username=username, password=password)

@pytest.fixture
def other_user(db, client):
	username = 'user2'
	password = 'password'

	return User.objects.create_user(username=username, password=password)