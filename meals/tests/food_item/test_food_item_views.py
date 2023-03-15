from meals.models import FoodItem

class TestFoodItemViews:

	# The user should not be able to create a FoodItem with the same name as an existing FoodItem.
	def test_duplicate_food_item_same_user(self, user, client):
		food_item_name = 'Milk'

		FoodItem.objects.create(food_item_name=food_item_name, user=user)
		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 1

		client.force_login(user)

		client.post('/food_items/new/', {
			'food_item_name': food_item_name
		})

		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 1

	# The user should be able to create a FoodItem with the same name as an existing FoodItem if the existing FoodItem belongs to a different user.
	def test_duplicate_food_item_different_users(self, user, other_user, client):
		food_item_name = 'Milk'

		FoodItem.objects.create(food_item_name=food_item_name, user=other_user)
		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 1

		client.force_login(user)

		client.post('/food_items/new/', {
			'food_item_name': food_item_name,
		})

		assert FoodItem.objects.filter(food_item_name=food_item_name).count() == 2

	def test_food_items_must_have_names(self, user, client):
		client.force_login(user)

		client.post('/food_items/new/', {
			'food_item_name': '',
		})

		assert FoodItem.objects.count() == 0