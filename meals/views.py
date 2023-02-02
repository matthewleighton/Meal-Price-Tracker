from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .forms import FoodItemForm, FoodPriceRecordForm
from .models import FoodItem, FoodPriceRecord

from pprint import pprint

def index(request):
	if not request.user.is_authenticated:
		return render(request, 'meals/home.html', {})	

	user = request.user
	food_items = FoodItem.objects.filter(user=user)

	context = {
		'food_items': food_items,
		'user': user
	}

	return render(request, 'meals/home.html', context)



def food_item_list(request):
	return HttpResponse('This is the food_item_list view.')


def food_item(request, food_item_id):
	food_item = get_object_or_404(FoodItem, pk=food_item_id)
	price_records = FoodPriceRecord.objects.filter(food_item=food_item)

	context = {
		'food_item': food_item,
		'price_records': price_records
	}

	return render(request, 'meals/food_item/info.html', context)

def new_food_item(request):
	if request.method == 'POST':
		form = FoodItemForm(request.POST)

		if form.is_valid():
			food_item = form.save(commit=False)
			food_item.user = request.user
			food_item.save()

			return redirect('/')

	else:
		form = FoodItemForm()

	context = {'form': form}
	

	return render(request, 'meals/food_item/new.html', context)

def new_food_price_record(request):
	if request.method == 'POST':
		form = FoodPriceRecordForm(request.POST)

		if form.is_valid():
			form.save()
			return redirect('/')

	else:
		form = FoodPriceRecordForm()

	context = {'form': form}

	return render(request, 'meals/food_price_record/new.html', context)


def meal_instance_list(request):
	return HttpResponse('This is the meal_instance_list view.')

def new_meal_instance(request):
	return HttpResponse('This is the new_meal_instance view.')


def meals_list(request):
	return HttpResponse('This is the meals_list view.')



def price_record_list(request):
	return HttpResponse('This is the price_record_list view.')