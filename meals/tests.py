from django.test import TestCase
from meals.models import Meal, MealInstance, FoodItem, StandardIngredient, FoodPriceRecord
from django.contrib.auth.models import User

from datetime import date, timedelta
from decimal import Decimal, getcontext

class MealTestCase(TestCase):
	def setUp(self):
		self.user1 = User.objects.create_user(username='user1', password='12345')
		self.client.login(username='user1', password='12345')

		self.user2 = User.objects.create_user(username='user2', password='67890')

		today = date.today()
		yesterday = today - timedelta(days=1)
		last_week = today - timedelta(days=7)
		
		# Create Meals
		self.porridge = Meal.objects.create(meal_name='Porridge', user=self.user1)
		self.toast 	 = Meal.objects.create(meal_name='Toast', user=self.user1)

		# Create FoodItems
		self.oats   = FoodItem.objects.create(food_item_name='Oats', user=self.user1)
		self.milk   = FoodItem.objects.create(food_item_name='Milk', user=self.user1)

		self.bread_slice = FoodItem.objects.create(food_item_name='Bread Slice', user=self.user1)
		self.butter = FoodItem.objects.create(food_item_name='Butter', user=self.user1)
		self.jam    = FoodItem.objects.create(food_item_name='Jam', user=self.user1)


		# Create StandardIngredients
		self.oats_ingredient = StandardIngredient.objects.create(meal=self.porridge, food_item=self.oats, quantity=50, unit='g')
		self.milk_ingredient = StandardIngredient.objects.create(meal=self.porridge, food_item=self.milk, quantity=100, unit='ml')

		self.bread_slice_ingredient = StandardIngredient.objects.create(meal=self.toast, food_item=self.bread_slice, quantity=2, unit='pc')
		self.butter_ingredient = StandardIngredient.objects.create(meal=self.toast, food_item=self.butter, quantity=20, unit='g')
		self.jam_ingredient  = StandardIngredient.objects.create(meal=self.toast, food_item=self.jam, quantity=30, unit='g')


		# Create FoodPriceRecords
		self.buy_oats1 = FoodPriceRecord.objects.create(food_item=self.oats, price_amount=0.50, currency='EUR', quantity=500,
												   unit='g', location='Lidl', date=today)


		self.buy_milk1 = FoodPriceRecord.objects.create(food_item=self.milk, price_amount=5.00, currency='EUR', quantity=1,
												   unit='l', location='Lidl', date=last_week)
		
		self.buy_milk2 = FoodPriceRecord.objects.create(food_item=self.milk, price_amount=1.00, currency='EUR', quantity=1,
												   unit='l', location='Lidl', date=today)

		self.buy_milk3 = FoodPriceRecord.objects.create(food_item=self.milk, price_amount=2.00, currency='EUR', quantity=1,
												   unit='l', location='Lidl', date=yesterday)

		# Create MealInstances
		MealInstance.objects.create(meal=self.porridge, date=today,     num_servings=1, rating=5, cook_time=10)
		MealInstance.objects.create(meal=self.porridge, date=yesterday, num_servings=1, rating=4, cook_time=10)

		MealInstance.objects.create(meal=self.toast, date=yesterday, num_servings=1, rating=3, cook_time=5)

	def test_food_item_get_newest_purchase(self):
		newest_purchase = self.milk.get_newest_purchase()
		self.assertEqual(newest_purchase, self.buy_milk2)

	def test_get_meal_standard_ingredients(self):
		standard_ingredients = self.porridge.standard_ingredients

		self.assertEqual(len(standard_ingredients), 2)

		self.assertTrue(self.oats_ingredient in standard_ingredients)
		self.assertTrue(self.milk_ingredient in standard_ingredients)
		self.assertFalse(self.jam_ingredient in standard_ingredients)


	def test_get_meal_food_items(self):
		food_items = self.porridge.get_food_items()

		self.assertEqual(len(food_items), 2)
		self.assertTrue(self.oats in food_items)
		self.assertTrue(self.milk in food_items)
		self.assertFalse(self.jam in food_items)


	def test_number_of_meal_instances(self):
		porridge_actual = len(self.porridge.meal_instances)
		toast_actual = len(self.toast.meal_instances)

		porridge_expected = 2
		toast_expected = 1

		self.assertEqual(porridge_actual, porridge_expected)
		self.assertEqual(toast_actual, toast_expected)


	def test_number_of_standard_ingredients(self):
		porridge_actual = len(self.porridge.standard_ingredients)
		toast_actual = len(self.toast.standard_ingredients)

		porridge_expected = 2
		toast_expected = 3

		self.assertEqual(porridge_actual, porridge_expected)
		self.assertEqual(toast_actual, toast_expected)

	def test_newest_meal_price_correct(self):
		porridge_actual = self.porridge.get_newest_price()
		porridge_expected = Decimal('0.15') # 50 grams of oats @ 50 cents per 500 grams, and 100ml milk @ 1 euro per litre.

		self.assertEqual(porridge_actual, porridge_expected)

	

	def test_meal_get_newest_ingredient_price_no_unit_conversion(self):
		oats_price = self.porridge.get_newest_ingredient_price(self.oats_ingredient)
		oats_expected = round(Decimal(0.05), 2)

		self.assertEqual(oats_price, oats_expected)

	def test_meal_get_newest_ingredient_price_with_unit_conversion(self):
		milk_price = self.porridge.get_newest_ingredient_price(self.milk_ingredient)
		milk_expected = round(Decimal(0.1), 2)

		self.assertEqual(milk_price, milk_expected)

	