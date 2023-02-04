from django.test import TestCase
from meals.models import Meal, MealInstance, FoodItem, StandardIngredient, FoodPriceRecord
from django.contrib.auth.models import User

from datetime import date, timedelta

class MealTestCase(TestCase):
	def setUp(self):
		self.user1 = User.objects.create_user(username='user1', password='12345')
		self.client.login(username='user1', password='12345')

		self.user2 = User.objects.create_user(username='user2', password='67890')

		today = date.today()
		yesterday = today - timedelta(days=1)
		
		# Create Meals
		porridge = Meal.objects.create(meal_name='Porridge', user=self.user1)
		toast 	 = Meal.objects.create(meal_name='Toast', user=self.user1)

		# Create FoodItems
		oats   = FoodItem.objects.create(food_item_name='Oats', user=self.user1)
		milk   = FoodItem.objects.create(food_item_name='Milk', user=self.user1)

		bread_slice = FoodItem.objects.create(food_item_name='Bread Slice', user=self.user1)
		butter = FoodItem.objects.create(food_item_name='Butter', user=self.user1)
		jam    = FoodItem.objects.create(food_item_name='Jam', user=self.user1)


		# Create StandardIngredients
		oats_ingredient = StandardIngredient.objects.create(meal=porridge, food_item=oats, quantity=50, unit='g')
		milk_ingredient = StandardIngredient.objects.create(meal=porridge, food_item=milk, quantity=100, unit='ml')

		bread_slice_ingredient = StandardIngredient.objects.create(meal=toast, food_item=bread_slice, quantity=2, unit='pc')
		butter_ingredient = StandardIngredient.objects.create(meal=toast, food_item=butter, quantity=20, unit='g')
		jam_ingredient  = StandardIngredient.objects.create(meal=toast, food_item=jam, quantity=30, unit='g')


		

		# Create MealInstances
		MealInstance.objects.create(meal=porridge, date=today,     num_servings=1, rating=5, cook_time=10)
		MealInstance.objects.create(meal=porridge, date=yesterday, num_servings=1, rating=4, cook_time=10)

		MealInstance.objects.create(meal=toast, date=yesterday, num_servings=1, rating=3, cook_time=5)




	def test_number_of_meal_instances(self):
		porridge = Meal.objects.filter(user=self.user1, meal_name='Porridge')[0]
		toast    = Meal.objects.filter(user=self.user1, meal_name='Toast')[0]

		porridge_actual = len(porridge.meal_instances)
		toast_actual = len(toast.meal_instances)

		porridge_expected = 2
		toast_expected = 1

		self.assertEqual(porridge_actual, porridge_expected)
		self.assertEqual(toast_actual, toast_expected)


	def test_number_of_standard_ingredients(self):
		porridge = Meal.objects.filter(user=self.user1, meal_name='Porridge')[0]
		toast    = Meal.objects.filter(user=self.user1, meal_name='Toast')[0]

		porridge_actual = len(porridge.standard_ingredients)
		toast_actual = len(toast.standard_ingredients)

		porridge_expected = 2
		toast_expected = 3

		self.assertEqual(porridge_actual, porridge_expected)
		self.assertEqual(toast_actual, toast_expected)

	# def test_average_cost(self):
	# 	porridge = Meal.objects.filter(user=self.user1, meal_name='Porridge')[0]