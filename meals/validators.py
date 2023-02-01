class MealValidators():
	
	def is_valid_unit(value):
		valid_units = [
			'g', # Gram
			'kg', # Kilogram
			'lb', # Pound
			'ml', # Millilitre
			'l' # Litre
			'pc' # Piece
			'cup', # Cup
			'tsp', # Teaspoon
			'tbsp' # Tablespoon
		]

		return True if value in valid_units else False
	
	def is_valid_currency(value):
		# TODO: Use CurrencyConverter package to get actual currency list.
		valid_currencies = ['EUR', 'GBP']

		return True if value in valid_currencies else False