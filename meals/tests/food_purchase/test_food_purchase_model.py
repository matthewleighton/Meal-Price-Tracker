from datetime import date, timedelta
from django.forms import ValidationError

import pytest

from meals.models import FoodItem, FoodPurchase
from meals.models.food_item import UserDuplicateFoodItemError

class TestFoodPurchaseModel:
	pass