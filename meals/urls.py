from django.urls import path
# from django.urls import re_path

from . import views
# from .views import FoodItemAutocomplete

urlpatterns = [

	path('', views.index, name='index'),

	path('meals/', views.meals_list, name='meals_list'),
	path('meals/new/', views.meals_new, name='meals_new'),
	path('meals/<int:meal_id>/', views.meals_item, name='meals_item'),
    path('meals/<int:meal_id>/delete/', views.meals_item_delete, name='meals_item_delete'),

	path('food_items/', views.food_item_list, name='food_item_list'),
	path('food_items/new/', views.new_food_item, name='new_food_item'),
	path('food_items/<int:food_item_id>/', views.food_item, name='food_item'),
    path('food_items/<int:ingredient_id>/delete/', views.ingredient_delete, name='ingredient_delete'),
    
	path('ingredients/new/<int:meal_id>', views.new_standard_ingredient, name='new_standard_ingredient'),

	# re_path(
	# 	r'^ingredients/autocomplete/$',
    #     FoodItemAutocomplete.as_view(),
    #     name='food_item_autocomplete',
	# ),
	
	path('purchases/', views.price_record_list, name='purchase_list'),
	path('purchases/new/', views.new_food_price_record, name='new_purchase'),

	path('meal_instances/', views.meal_instance_list, name='meal_instance_list'),
	path('meal_instances/new/', views.new_meal_instance, name='new_meal_instance')
    


]