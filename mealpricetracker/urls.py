"""mealpricetracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from meals import views as meals_views

urlpatterns = [
    # path('meals/', include('meals.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', meals_views.index, name='index'),
	
    path('ingredients', meals_views.food_item_list, name='food_item_list'),
    path('ingredients/new', meals_views.new_food_item, name='new_food_item'),
	path('ingredients/<int:food_item_id>', meals_views.food_item, name='food_item'),

    path('purchases', meals_views.price_record_list, name='price_record_list'),
    path('purchases/new', meals_views.new_food_price_record, name='new_food_price_record'),

    path('mean_instances', meals_views.meal_instance_list, name='meal_instance_list'),
	path('meal_instance/new', meals_views.new_meal_instance, name='new_meal_instance'),
	
    path('my_meals', meals_views.meals_list, name='meals_list')
]
