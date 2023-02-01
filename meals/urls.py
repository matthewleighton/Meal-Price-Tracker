from django.urls import path

from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('food_item/new', views.new_food_item, name='new_food_item'),
	path('food_price_record/new', views.new_food_price_record, name='new_food_price_record')
]