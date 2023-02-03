from django.test import TestCase
from meals.models import Meal, MealInstance, FoodItem, StandardIngredient, FoodPriceRecord
from django.contrib.auth.models import User

from datetime import date, timedelta

class MealTestCase(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='testuser', password='12345')
		self.client.login(username='testuser', password='12345')

		today = date.today()
		yesterday = today - timedelta(days=1)
		
		# Create Meals
		porridge = Meal.objects.create(meal_name='Porridge', user=self.user)

		# Create FoodItems
		oats = FoodItem.objects.create(food_item_name='Oats', user=self.user)
		milk = FoodItem.objects.create(food_item_name='Milk', user=self.user)

		# Create StandardIngredients
		oats_ingredient = StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g')
		milk_ingredient = StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')


		

		# Create MealInstances
		MealInstance.objects.create(meal=porridge, date=today,     num_servings=1, rating=5, cook_time=10)
		MealInstance.objects.create(meal=porridge, date=yesterday, num_servings=1, rating=4, cook_time=10)



	def test_number_of_meal_instances(self):
		porridge = Meal.objects.filter(user=self.user, meal_name='Porridge')[0]

		actual = len(porridge.get_meal_instances())
		expected = 2

		self.assertEqual(actual, expected)

	def test_number_of_standard_ingredients(self):
		porridge = Meal.objects.filter(user=self.user, meal_name='Porridge')[0]

		actual = porridge.count_standard_ingredients()
		expected = 2

		self.assertEqual(actual, expected)		

	# def test_average_cost(self):
	# 	porridge = Meal.objects.filter(user=self.user, meal_name='Porridge')[0]