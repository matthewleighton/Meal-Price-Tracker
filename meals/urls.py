from django.urls import path

from . import views

urlpatterns = [

	path('', views.index, name='index'),

	path('meals/', views.meals_list, name='meals_list'),
	path('meals/new/', views.meals_new, name='meals_new'),

	path('ingredients/', views.food_item_list, name='food_item_list'),
	path('ingredients/new/', views.new_food_item, name='new_food_item'),
	path('ingredients/<int:food_item_id>/', views.food_item, name='food_item'),
	
	path('purchases/', views.price_record_list, name='purchase_list'),
	path('purchases/new/', views.new_food_price_record, name='new_purchase'),

	path('meal_instances/', views.meal_instance_list, name='meal_instance_list'),
	path('meal_instances/new/', views.new_meal_instance, name='new_meal_instance')

]