a = 3
b = ['K', 'Q']


def alter_a (x, card):
	global a, b
	# trying to chg the int
	x = 5

	#trying to chg the list
	card.append('J')

	print(x)
	print(a)

	print(card)
	print(b)

	return 0

#this is the main function
alter_a(a, b)