def get_unit_conversion_factor(from_unit, to_unit):
	"""
	Converts from one unit to another.
	"""
	conversion_factor = 1

	from_unit = from_unit.lower()
	to_unit = to_unit.lower()

	if from_unit == to_unit:
		return conversion_factor

	if from_unit == 'oz':
		if to_unit == 'lb':
			conversion_factor = 1 / 16
		elif to_unit == 'g':
			conversion_factor = 28.3495
		elif to_unit == 'kg':
			conversion_factor = 0.0283495
	elif from_unit == 'lb':
		if to_unit == 'oz':
			conversion_factor = 16
		elif to_unit == 'g':
			conversion_factor = 453.592
		elif to_unit == 'kg':
			conversion_factor = 0.453592
	elif from_unit == 'g':
		if to_unit == 'oz':
			conversion_factor = 0.035274
		elif to_unit == 'lb':
			conversion_factor = 0.00220462
		elif to_unit == 'kg':
			conversion_factor = 0.001
	elif from_unit == 'kg':
		if to_unit == 'oz':
			conversion_factor = 35.274
		elif to_unit == 'lb':
			conversion_factor = 2.20462
		elif to_unit == 'g':
			conversion_factor = 1000
	elif from_unit == 'ml':
		if to_unit == 'l':
			conversion_factor = 0.001
	elif from_unit == 'l':
		if to_unit == 'ml':
			conversion_factor = 1000

	return conversion_factor