from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import FoodItemForm
from .models import FoodItem

from pprint import pprint

# Create your views here.

def index(request):

	user = request.user
	food_items = FoodItem.objects.filter(user=user)

	context = {
		'food_items': food_items,
		'user': user
	}

	return render(request, 'meals/home.html', context)

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