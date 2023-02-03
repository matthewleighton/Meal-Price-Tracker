from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from .forms import FoodItemForm, FoodPriceRecordForm, MealForm, MealInstanceForm
from .models import FoodItem, FoodPriceRecord, Meal, MealInstance

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

##############################################################################
#---------------------------------- Food Item -------------------------------#
##############################################################################

def food_item_list(request):
	user = request.user
	if not user.is_authenticated:
		return redirect('/')

	food_items = FoodItem.objects.filter(user=user)
	form = FoodItemForm()

	context = {
		'form': form,
		'food_items': food_items
	}

	return render(request, 'meals/food_item/list.html', context)

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

			next = request.POST.get('next', '/')
			return HttpResponseRedirect(next)

	else:
		form = FoodItemForm()

	context = {'form': form}
	

	return render(request, 'meals/food_item/new.html', context)

##############################################################################
#-------------------------- Food Price Record -------------------------------#
##############################################################################

def price_record_list(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseRedirect('/')

	price_records = FoodPriceRecord.objects.filter(food_item__user__exact=user)

	context = {
		'price_records': price_records
	}

	return render(request, 'meals/food_price_record/list.html', context=context)

def new_food_price_record(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/')
	
	if request.method == 'POST':
		form = FoodPriceRecordForm(request.POST)

		if form.is_valid():
			form.save()
			return redirect('/')

	else:
		form = FoodPriceRecordForm()

	context = {'form': form}

	return render(request, 'meals/food_price_record/new.html', context)

##############################################################################
#------------------------------- Meal Instance ------------------------------#
##############################################################################

def meal_instance_list(request):
	user = request.user
	if not user.is_authenticated:
		return redirect('/')

	meal_instances = MealInstance.objects.filter(meal__user__exact=user)

	context = {
		'user': user,
		'meal_instances': meal_instances
	}

	return render(request, 'meals/meal_instance/list.html', context)

def new_meal_instance(request):
	if not request.user.is_authenticated:
		return redirect('/')

	if request.method == 'POST':
		form = MealInstanceForm(request.POST)

		if form.is_valid():
			meal_instance = form.save()
			redirect_location = request.POST.get('redirect_location', '/')
			return HttpResponseRedirect(redirect_location)
	else:
		form = MealInstanceForm()	

	context = {
		'form': form
	}

	return render(request, 'meals/meal_instance/new.html', context)

##############################################################################
#------------------------------------ Meal ----------------------------------#
##############################################################################

def meals_list(request):
	user = request.user
	if not user.is_authenticated:
		return redirect('/')

	meals = Meal.objects.filter(user=user)
	form = MealForm()

	context = {
		'form': form,
		'meals': meals
	}

	return render(request, 'meals/meals/list.html', context)

def meals_new(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseRedirect('/')

	if request.method == 'POST':
		form = MealForm(request.POST)

		user = request.user

		if form.is_valid():
			meal = form.save(commit=False)
			meal.user = request.user
			meal.save()

			redirect_location = request.POST.get('redirect_location', '/')
			return HttpResponseRedirect(redirect_location)

	else:
		return HttpResponseRedirect('/')

def meals_item(request, meal_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseRedirect('/')

	meal = get_object_or_404(Meal, pk=meal_id)

	if not meal.user == user:
		return HttpResponseRedirect('/')

	context = {
		'meal': meal,
		'meal_instances': meal.get_meal_instances()
	}

	return render(request, 'meals/meals/item.html', context)