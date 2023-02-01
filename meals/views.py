from django.shortcuts import render
from django.http import HttpResponse

from pprint import pprint

# Create your views here.

def index(request):
	context = {
		'user': request.user
	}

	return render(request, 'meals/home.html', context)