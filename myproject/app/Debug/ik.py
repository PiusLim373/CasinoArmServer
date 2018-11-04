import time
class chain1:
	def move_to(coordinate):
		time.sleep(1)
		return "Arm Moved"
	def dispense():
		print("dispensing card")
		return "dispensing card"
	def grip(a):
		if a == 1:
			print("gripper closed")
			return "gripper closed"
		elif a == 0:
			print("gripper opened")
			return "gripper opened"
		return "Card Picked"
	class deck:
		def move_to(coordinate):
			time.sleep(1)
			return "Arm Moved"
	class deck1:
		def move_to(coordinate):
			time.sleep(1)
			return "Arm Moved"
	def dynamixel_write(coordinate):
		return 0



