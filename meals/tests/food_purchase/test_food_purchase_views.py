import datetime
from django.urls import reverse
import pytest
from meals.models import FoodItem
from meals.models.food_purchase import FoodPurchase

class TestFoodPurchaseViews:
    
	def test_delete_existing_purchase(self, user, client):
		food_item = FoodItem.objects.create(name='Milk', user=user)
		purchase = FoodPurchase.objects.create(
			food_item=food_item,
			price_amount=1.00,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		assert FoodPurchase.objects.count() == 1

		client.force_login(user)
		client.post(f'/purchases/{purchase.id}/delete/')

		assert FoodPurchase.objects.count() == 0

	def test_delete_non_existing_purchase(self, user, client):
		food_item = FoodItem.objects.create(name='Milk', user=user)
		FoodPurchase.objects.create(
			food_item=food_item,
			price_amount=1.00,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		assert FoodPurchase.objects.count() == 1
		
		client.force_login(user)
		response = client.post(f'/purchases/123/delete/')

		assert response.status_code == 404
		assert FoodPurchase.objects.count() == 1

	def test_delete_purchase_of_other_user(self, user, other_user, client):
		food_item = FoodItem.objects.create(name='Milk', user=other_user)
		purchase = FoodPurchase.objects.create(
			food_item=food_item,
			price_amount=1.00,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		assert FoodPurchase.objects.count() == 1

		client.force_login(user)
		response = client.post(f'/purchases/{purchase.id}/delete/')

		assert response.status_code == 403
		assert FoodPurchase.objects.count() == 1

	@pytest.mark.parametrize('update_field, update_value', [
		('price_amount', 2.00),
		('quantity', 50),
		('unit', 'kg'),
		('location', 'Lidl'),
		('date',  datetime.date(2020, 1, 1)),
		('currency', 'GBP')
	])
	def test_edit_existing_purchase(self, user, client, update_field, update_value):
		food_item = FoodItem.objects.create(name='Milk', user=user)
		purchase = FoodPurchase.objects.create(
			food_item=food_item,
			price_amount=1.00,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		assert FoodPurchase.objects.count() == 1

		new_data = purchase.__dict__
		new_data[update_field] = update_value
		new_data['food_item'] = new_data['food_item_id']

		client.force_login(user)
		url = reverse('purchase', args=[purchase.id])
		client.post(url, new_data)

		assert FoodPurchase.objects.count() == 1
		assert FoodPurchase.objects.first().__dict__[update_field] == update_value

	def test_edit_other_user_purchase(self, user, other_user, client):
		original_price = 1.00

		food_item = FoodItem.objects.create(name='Milk', user=other_user)
		purchase = FoodPurchase.objects.create(
			food_item=food_item,
			price_amount=original_price,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		assert FoodPurchase.objects.count() == 1

		new_price_amount = 2.00

		url = reverse('purchase', args=[purchase.id])

		client.force_login(user)
		response = client.post(url, {
			'food_item': food_item.id,
			'price_amount': new_price_amount,
			'quantity': 2.00,
			'unit': 'l',
			'location': 'Rewe',
			'date': '2020-01-01',
			'currency': 'EUR'
		})

		assert response.status_code == 403
		assert FoodPurchase.objects.count() == 1
		assert FoodPurchase.objects.first().price_amount == original_price

	# Making sure that the user cannot pass the food_item_id of another user.
	def test_cannot_change_purchase_food_item_to_food_item_of_other_user(self, user, other_user, client):
		my_original_price = 123.00
		other_user_original_price = 1.00

		new_price = 2.00

		my_food_item = FoodItem.objects.create(name='Cheese', user=user)
		my_purchase = FoodPurchase.objects.create(
			food_item=my_food_item,
			price_amount=my_original_price,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		other_user_food_item = FoodItem.objects.create(name='Milk', user=other_user)
		other_user_purchase = FoodPurchase.objects.create(
			food_item=other_user_food_item,
			price_amount=other_user_original_price,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		url = reverse('purchase', args=[my_purchase.id])
		client.force_login(user)

		response = client.post(url, {
			'food_item': other_user_food_item.id,
			'price_amount': new_price,
			'quantity': 2.00,
			'unit': 'l',
			'location': 'Rewe',
			'date': '2020-01-01',
			'currency': 'EUR'
		})

		assert FoodPurchase.objects.get(id=my_purchase.id).food_item == my_food_item

	def test_edit_non_existing_food_purchase(self, user, client):
		food_item = FoodItem.objects.create(name='Milk', user=user)
		FoodPurchase.objects.create(
			food_item=food_item,
			price_amount=1.00,
			quantity=1.00,
			unit='l',
			location='Rewe',
			date='2020-01-01',
			currency='EUR'
		)

		assert FoodPurchase.objects.count() == 1

		new_price_amount = 2.00

		url = reverse('purchase', args=[123])

		client.force_login(user)
		response = client.post(url, {
			'food_item': food_item.id,
			'price_amount': new_price_amount,
			'quantity': 2.00,
			'unit': 'l',
			'location': 'Rewe',
			'date': '2020-01-01',
			'currency': 'EUR'
		})

		assert response.status_code == 404
		assert FoodPurchase.objects.count() == 1
		assert FoodPurchase.objects.first().price_amount == 1.00