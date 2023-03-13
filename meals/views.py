from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.forms import formset_factory


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

	food_items = FoodItem.objects.filter(user=user)
	form = FoodItemForm()

	context = {
		'form': form,
		'food_items': food_items
	}

	return render(request, 'meals/food_item/list.html', context)

# View a single food item.
def food_item(request, food_item_id):
	food_item = get_object_or_404(FoodItem, pk=food_item_id)
	price_records = FoodPriceRecord.objects.filter(food_item=food_item)

	context = {
		'food_item': food_item,
		'price_records': price_records
	}

	return render(request, 'meals/food_item/info.html', context)

# Create a new food item.
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
		if not food_item_id:
			food_item = FoodItem.objects.create(
				user=user,
				food_item_name=food_item_name
			)
		else:
			food_item = FoodItem.objects.get(pk=food_item_id)

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

	standard_ingredients = StandardIngredient.objects.filter(meal=meal)

	if not meal.user == user:
		return HttpResponseRedirect('/')
	
	context = {
		'meal': meal,
		'standard_ingredients': standard_ingredients,
		'meal_instances': meal.meal_instances,
	}

	return render(request, 'meals/meals/item.html', context)