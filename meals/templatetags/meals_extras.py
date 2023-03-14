from django import template

from pprint import pprint

register = template.Library()

@register.simple_tag
def call_method(obj, method_name, *args):
	method = getattr(obj, method_name)
	return method(*args)