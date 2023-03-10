from datetime import date, timedelta

from meals.models import FoodItem, FoodPriceRecord

def test_food_item_get_newest_purchase(user):
	milk = FoodItem.objects.create(food_item_name='Milk', user=user)

	today = date.today()
	last_week = date.today() - timedelta(days=7)
	last_year = date.today() - timedelta(days=365)

	old_milk 	= FoodPriceRecord.objects.create(food_item=milk, price_amount=5.00, currency='EUR', quantity=1, unit='l', location='Aldi', date=last_year)
	new_milk 	= FoodPriceRecord.objects.create(food_item=milk, price_amount=1.00, currency='EUR', quantity=1, unit='l', location='Aldi', date=today)
	middle_milk = FoodPriceRecord.objects.create(food_item=milk, price_amount=2.00, currency='EUR', quantity=1, unit='l', location='Aldi', date=last_week)

	assert milk.get_newest_purchase() == new_milk