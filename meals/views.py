from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.forms import formset_factory
from django.views.decorators.http import require_http_methods


from dal import autocomplete

from .forms import FoodItemForm, FoodPurchaseForm, MealForm, MealInstanceForm, StandardIngredientForm
from .models import FoodItem, FoodPurchase, Meal, MealInstance, StandardIngredient

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

	food_items = FoodItem.objects.filter(user=user).order_by('name')
	form = FoodItemForm(user=user, request=request)

	context = {
		'form': form,
		'food_items': food_items
	}

	return render(request, 'meals/food_item/list.html', context)

# View a single food item.
def food_item(request, food_item_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	food_item = get_object_or_404(FoodItem, pk=food_item_id)

	if food_item.user != user:
		return HttpResponseForbidden()

	price_records = FoodPurchase.objects.filter(food_item=food_item)

	food_purchase_form = FoodPurchaseForm(initial={'food_item': food_item}, user=user)
	food_purchase_form.fields['food_item'].widget = forms.HiddenInput()
	food_purchase_form.initial['food_item'] = food_item

	meals = food_item.meals

	context = {
		'food_item': food_item,
		'meals': meals,
		'price_records': price_records,
		'food_purchase_form': food_purchase_form
	}

	return render(request, 'meals/food_item/info.html', context)

# Create a new food item.
@require_http_methods(['POST'])
def new_food_item(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()

	food_item_form = FoodItemForm(request.POST, user=user, request=request)

	if food_item_form.is_valid():
		food_item_form.save(commit=True)

		next = request.POST.get('next', '/')
		return HttpResponseRedirect(next)

	return HttpResponse(status=201)

def food_item_delete(request, food_item_id):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	food_item = get_object_or_404(FoodItem, pk=food_item_id)

	if food_item.user != user:
		return HttpResponseForbidden()
	
	food_item.delete()

	previous_page = request.META.get('HTTP_REFERER', '/')
	return redirect(previous_page)

class FoodItemAutocomplete(autocomplete.Select2QuerySetView):
	def get_queryset(self):

		print('self.q: ', self.q)

		if not self.request.user.is_authenticated:
			return FoodItem.objects.none()

		qs = FoodItem.objects.filter(user=self.request.user)

		if self.q:
			qs = qs.filter(name__istartswith=self.q)

		return qs

##############################################################################
#---------------------------- Food Purchase ---------------------------------#
##############################################################################

def price_record_list(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseRedirect('/')

	price_records = FoodPurchase.objects.filter(food_item__user__exact=user).order_by('-date')

	food_purchase_form = FoodPurchaseForm(user=user)


	context = {
		'food_purchase_form': food_purchase_form,
		'food_purchase_form_toggle': True,
		'price_records': price_records
	}

	return render(request, 'meals/food_purchase/list.html', context=context)

def new_food_purchase(request):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseRedirect('/')
	
	if request.method == 'POST':
		food_purchase_form = FoodPurchaseForm(request.POST, user=user)

		if food_purchase_form.is_valid():
			food_purchase_form.save()
			
			previous_page = request.META.get('HTTP_REFERER', '/')
			return redirect(previous_page)

	else:
		food_purchase_form = FoodPurchaseForm(user=user)

	context = {'food_purchase_form': food_purchase_form}

	return render(request, 'meals/food_purchase/new.html', context)

def food_purchase_detail(request, food_purchase_id):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseForbidden()

	food_purchase = get_object_or_404(FoodPurchase, pk=food_purchase_id)

	if food_purchase.food_item.user != user:
		return HttpResponseForbidden()
	
	if request.method == 'POST':
		
		food_purchase_form = FoodPurchaseForm(request.POST, instance=food_purchase, user=user)


		if food_purchase_form.is_valid():
			food_purchase_form.save()

			food_item_url = reverse('food_item', args=[food_purchase.food_item.id])
			return redirect(food_item_url)

	else:
		food_purchase_form = FoodPurchaseForm(instance=food_purchase, user=user)
		food_purchase_form.initial['food_item'] = food_purchase.food_item

	food_purchase_form.fields['food_item'].widget = forms.HiddenInput()

	context = {
		'food_purchase': food_purchase,
		'food_purchase_form': food_purchase_form
	}

	return render(request, 'meals/food_purchase/detail.html', context)

def food_purchase_delete(request, food_purchase_id):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	food_purchase = get_object_or_404(FoodPurchase, pk=food_purchase_id)

	if food_purchase.food_item.user != user:
		return HttpResponseForbidden()
	
	food_purchase.delete()

	previous_page = request.META.get('HTTP_REFERER', '/')
	return redirect(previous_page)


##############################################################################
#------------------------------- Meal Instance ------------------------------#
##############################################################################

def meal_instance_list(request):
	user = request.user
	if not user.is_authenticated:
		return redirect('/')

	meal_instances = MealInstance.objects.filter(meal__user__exact=user).order_by('-date')

	if request.method == 'POST':
		meal_instance_form = MealInstanceForm(request.POST, user=user)

		if meal_instance_form.is_valid():
			meal_instance_form.save()
	
	else:
		meal_instance_form = MealInstanceForm(user=user)

	context = {
		'user': user,
		'meal_instances': meal_instances,
		'meal_instance_form': meal_instance_form
	}

	return render(request, 'meals/meal_instance/list.html', context)

def new_meal_instance(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	if request.method == 'POST':
		meal_instance_form = MealInstanceForm(request.POST, user=user)

		if meal_instance_form.is_valid():
			meal_instance_form.save()

			redirect_url = reverse_lazy('meal_instance_list')
			return HttpResponseRedirect(redirect_url)

	else:
		meal_instance_form = MealInstanceForm(user=user)	

	context = {
		'meal_instance_form': meal_instance_form
	}

	return render(request, 'meals/meal_instance/new.html', context)

# Delete a meal instance, specified by its ID.
def meal_instance_delete(request, meal_instance_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()

	meal_instance = get_object_or_404(MealInstance, pk=meal_instance_id)

	if not meal_instance.meal.user == user:
		return HttpResponseForbidden()
	
	meal_instance.delete()

	previous_page = request.META.get('HTTP_REFERER', '/')
	return redirect(previous_page)

##############################################################################
#------------------------------------ Meal ----------------------------------#
##############################################################################

def meal_list(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponse(status=401)

	meals = Meal.objects.filter(user=user)

	StandardIngredientFormSet = formset_factory(StandardIngredientForm, extra=0)

	if request.method == 'POST':
		meal_form = MealForm(request.POST)
		ingredient_formset = StandardIngredientFormSet(request.POST, request.FILES, prefix='ingredient', form_kwargs={'user': user})

		if meal_form.is_valid():
			meal = meal_form.save(user=user, commit=False)

			for ingredient_form in ingredient_formset:
				ingredient_form.instance.meal = meal

			if ingredient_formset.is_valid():
				meal.save()

				for ingredient_form in ingredient_formset:
					ingredient_form.save(meal=meal)

				return redirect('meals_item', meal_id=meal.id)
			
	else:
		meal_form = MealForm()
		ingredient_formset = StandardIngredientFormSet(prefix='ingredient', form_kwargs={'user': user})

	context = {
		'meal_form': meal_form,
		'ingredient_formset': ingredient_formset,
		'meals': meals
	}

	return render(request, 'meals/meals/list.html', context)

def meals_item(request, meal_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponse(status=401)
	
	meal = get_object_or_404(Meal, pk=meal_id)
	
	if not meal.user == user:
		return HttpResponseForbidden()
	
	standard_ingredients = StandardIngredient.objects.filter(meal=meal)

	if request.method == 'POST':
		
		form_type = request.POST.get('form_type')
		
		if form_type == 'meal_instance':
			meal_instance_form = MealInstanceForm(request.POST, user=user)
			standard_ingredient_form = StandardIngredientForm(meal=meal, user=user)

			if meal_instance_form.is_valid():
				meal_instance_form.save()
				meal_instance_form = MealInstanceForm(initial={'meal': meal}, user=user)
		
		elif form_type == 'standard_ingredient':
			standard_ingredient_form = StandardIngredientForm(request.POST, meal=meal, user=user)
			meal_instance_form = MealInstanceForm(initial={'meal': meal}, user=user)

			if standard_ingredient_form.is_valid():
				standard_ingredient_form.save()
				standard_ingredient_form = StandardIngredientForm(meal=meal, user=user)
	
	else:
		meal_instance_form = MealInstanceForm(initial={'meal': meal}, user=user)
		standard_ingredient_form = StandardIngredientForm(meal=meal, user=user)

	meal_instance_form.fields['meal'].widget = forms.HiddenInput()
	
	context = {
		'hide_meal_instance_name': True,
		'meal': meal,
		'standard_ingredients': standard_ingredients,
		'meal_instances': meal.meal_instances,
		'standard_ingredients_form': standard_ingredient_form,
		'meal_instance_form': meal_instance_form
	}

	return render(request, 'meals/meals/item.html', context)

def meals_item_delete(request, meal_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	meal = get_object_or_404(Meal, pk=meal_id)

	if not meal.user == user:
		return HttpResponseForbidden()

	meal.delete()
	
	previous_page = request.META.get('HTTP_REFERER', '/')
	return redirect(previous_page)

##############################################################################
#--------------------------------- Ingredient -------------------------------#
##############################################################################

def ingredient(request, ingredient_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponse(status=401)

	ingredient = get_object_or_404(StandardIngredient, pk=ingredient_id)

	if not ingredient.meal.user == user:
		return HttpResponseForbidden()

	if request.method == 'POST':
		standard_ingredient_form = StandardIngredientForm(request.POST, instance=ingredient, user=user)

		if standard_ingredient_form.is_valid():
			ingredient = standard_ingredient_form.save()

			return redirect(reverse('meals_item', args=[ingredient.meal.id]))
	else:
		standard_ingredient_form = StandardIngredientForm(instance=ingredient, user=user)
		
	standard_ingredient_form.fields['food_item'].widget = forms.HiddenInput()
	standard_ingredient_form.initial['food_item'] = ingredient.food_item
	
	context = {
		'ingredient': ingredient,
		'standard_ingredient_form': standard_ingredient_form
	}

	return render(request, 'meals/ingredient/item.html', context)

def ingredient_delete(request, ingredient_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	ingredient = get_object_or_404(StandardIngredient, pk=ingredient_id)

	if not ingredient.meal.user == user:
		return HttpResponseForbidden()

	ingredient.delete()

	meal_name = ingredient.meal
	food_item_name = ingredient.food_item.name

	message = f'{meal_name} ingredient "{food_item_name}" has been deleted!'
	messages.success(request, message)

	previous_page = request.META.get('HTTP_REFERER', '/')
	return redirect(previous_page)