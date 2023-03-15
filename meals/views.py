from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.forms import formset_factory
from django.views.decorators.http import require_http_methods


from dal import autocomplete

from .forms import FoodItemForm, FoodPriceRecordForm, MealForm, MealInstanceForm, StandardIngredientForm
from .models import FoodItem, FoodPriceRecord, Meal, MealInstance, StandardIngredient

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

	food_items = FoodItem.objects.filter(user=user).order_by('food_item_name')
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

	price_records = FoodPriceRecord.objects.filter(food_item=food_item)

	food_price_record_form = FoodPriceRecordForm(initial={'food_item': food_item}, user=user)
	food_price_record_form.fields['food_item'].widget = forms.HiddenInput()
	food_price_record_form.fields['new_food_item'].widget = forms.HiddenInput()

	meals = food_item.meals

	context = {
		'food_item': food_item,
		'meals': meals,
		'price_records': price_records,
		'food_price_record_form': food_price_record_form
	}

	return render(request, 'meals/food_item/info.html', context)

# Create a new food item.
@require_http_methods(['POST'])
def new_food_item(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()

	if request.method == 'POST':
		food_item_form = FoodItemForm(request.POST, user=user, request=request)

		if food_item_form.is_valid():
			food_item_form.save(commit=True)

			next = request.POST.get('next', '/')
			return HttpResponseRedirect(next)

	else:
		food_item_form = FoodItemForm(user=user, request=request)

	context = {'form': food_item_form}
	

	return render(request, 'meals/food_item/new.html', context)

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
			qs = qs.filter(food_item_name__istartswith=self.q)

		return qs

##############################################################################
#-------------------------- Food Price Record -------------------------------#
##############################################################################

def price_record_list(request):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseRedirect('/')

	price_records = FoodPriceRecord.objects.filter(food_item__user__exact=user).order_by('-date')

	food_price_record_form = FoodPriceRecordForm(user=user)


	context = {
		'food_price_record_form': food_price_record_form,
		'price_records': price_records
	}

	return render(request, 'meals/food_price_record/list.html', context=context)

def new_food_price_record(request):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseRedirect('/')
	
	if request.method == 'POST':
		form = FoodPriceRecordForm(request.POST, user=user)

		if form.is_valid():
			form.save()
			
			previous_page = request.META.get('HTTP_REFERER', '/')
			return redirect(previous_page)

	else:
		form = FoodPriceRecordForm(user=user)

	context = {'form': form}

	return render(request, 'meals/food_price_record/new.html', context)

##############################################################################
#------------------------------- Meal Instance ------------------------------#
##############################################################################

def meal_instance_list(request):
	user = request.user
	if not user.is_authenticated:
		return redirect('/')

	meal_instances = MealInstance.objects.filter(meal__user__exact=user).order_by('-date')

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
		return redirect('/')

	if request.method == 'POST':
		form = MealInstanceForm(user, request.POST)

		if form.is_valid():
			meal_instance = form.save()
			previous_page = request.META.get('HTTP_REFERER', '/')
			return HttpResponseRedirect(previous_page)
	else:
		form = MealInstanceForm(user=user)	

	context = {
		'form': form
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

def meals_list(request):
	user = request.user
	if not user.is_authenticated:
		return redirect('/')

	meals = Meal.objects.filter(user=user)
	meal_form = MealForm()
	IngrdientFormset = formset_factory(StandardIngredientForm, extra=0)

	context = {
		'meal_form': meal_form,
		'ingredient_formset': IngrdientFormset(prefix='ingredient'),
		'meals': meals
	}

	return render(request, 'meals/meals/list.html', context)

@require_POST
def meals_new(request):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseRedirect('/')
	
	meal_form = MealForm(request.POST)
	StandardIngredientFormSet = formset_factory(StandardIngredientForm)
	ingredient_formset = StandardIngredientFormSet(request.POST, request.FILES, prefix='ingredient')

	if not meal_form.is_valid() or not ingredient_formset.is_valid():
		previous_page = request.META.get('HTTP_REFERER', '/')
		return redirect(previous_page)

	# Check that the user is the owner of the food items.
	for form in ingredient_formset:
		food_item_id = form.cleaned_data.get('food_item_id')

		if food_item_id:
			try:
				food_item = FoodItem.objects.get(pk=food_item_id)
			except:
				return HttpResponseForbidden() # TODO: Perhaps a more suitable error code?
			
			if food_item.user != user:
				return HttpResponseForbidden()

	# Create the meal
	meal = Meal.objects.create(
		user=user,
		meal_name=meal_form.cleaned_data.get('meal_name'),
	)

	# Create the ingredients
	for form in ingredient_formset:
		food_item_id = form.cleaned_data.get('food_item_id')
		food_item_name = form.cleaned_data.get('food_item_name')

		quantity = form.cleaned_data.get('quantity')
		unit = form.cleaned_data.get('unit')

		# If the food_item does not already exist, create it.
		if not food_item_id and food_item_name:
			food_item = FoodItem.objects.create(
				user=user,
				food_item_name=food_item_name
			)
		elif food_item_id:
			food_item = FoodItem.objects.get(pk=food_item_id)
		else:
			continue

		StandardIngredient.objects.create(
			meal=meal,
			food_item=food_item,
			quantity=quantity,
			unit=unit
		)

	messages.success(request, f'Meal "{meal.meal_name}" has been created!')
	return redirect(reverse('meals_item', args=[meal.id]))

def meals_item(request, meal_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseRedirect('/')
	
	meal = get_object_or_404(Meal, pk=meal_id)
	
	if not meal.user == user:
		return HttpResponseRedirect('/')
	
	standard_ingredients = StandardIngredient.objects.filter(meal=meal)
	
	meal_instance_form = MealInstanceForm(initial={'meal': meal}, user=user)
	meal_instance_form.fields['meal'].widget = forms.HiddenInput()
	
	context = {
		'meal': meal,
		'standard_ingredients': standard_ingredients,
		'meal_instances': meal.meal_instances,
		'standard_ingredients_form': StandardIngredientForm(),
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

def new_standard_ingredient(request, meal_id):
	user = request.user

	if not user.is_authenticated:
		return HttpResponseForbidden()

	meal = get_object_or_404(Meal, pk=meal_id)

	if not meal.user == user:
		return HttpResponseForbidden()
		
	if request.method == 'POST':
		form = StandardIngredientForm(request.POST)
		# form.set_meal(meal)

		if form.is_valid():
			form.save(meal=meal, user=user)
			return redirect(reverse('meals_item', args=[meal_id]))
		
	else:
		form = StandardIngredientForm()

	context = {}

	return render(request, 'meals/ingredient/new.html', context)




def ingredient_delete(request, ingredient_id):
	user = request.user
	if not user.is_authenticated:
		return HttpResponseForbidden()
	
	ingredient = get_object_or_404(StandardIngredient, pk=ingredient_id)

	if not ingredient.meal.user == user:
		return HttpResponseForbidden()

	ingredient.delete()

	meal_name = ingredient.meal
	food_item_name = ingredient.food_item.food_item_name

	message = f'{meal_name} ingredient "{food_item_name}" has been deleted!'
	messages.success(request, message)

	previous_page = request.META.get('HTTP_REFERER', '/')
	return redirect(previous_page)