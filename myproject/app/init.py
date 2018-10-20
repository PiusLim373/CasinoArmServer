from flask import Flask, render_template, request, jsonify
import requests
import time
import json
import os
import subprocess
from pprint import pprint
import serial
import collections
<<<<<<< HEAD
<<<<<<< HEAD
from Debug import pakzan
print("before IK")
import ik
print("after IK")
<<<<<<< HEAD
=======
from arm_pos import ik
>>>>>>> 9193f838574d699465b1c568b9aa26472eae5554
=======
from Debug import ik, pakzan
#from arm_pos import ik

>>>>>>> parent of d451ae9... after full run 1.0
=======
from Debug import ik, pakzan
#from arm_pos import ik

>>>>>>> parent of d451ae9... after full run 1.0
=======
>>>>>>> parent of a9ac3bf... Merge branch 'master' of https://github.com/PiusLim373/CasinoArmServer
app = Flask(__name__)

Player1Position = []
Player2Position = []
Player3Position = []

Player1Card = []
Player2Card = []
Player3Card = []

Player1CardValue = 0
Player2CardValue = 0
Player3CardValue = 0

ArmPosition = [0, 0, 0]   #This is position of Arm's Card deck
ArmCard = []
ArmCardValue = 0
CardStationPosition = [1,2,3]

Jumbotron_title = ""
Jumbotron_text1 = ""
Jumbotron_text2 = ""
ResetBtn = ""

test_i = 0
decision = ""
ActivateArduino = "NO"
ArduinoData = ""

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> parent of a9ac3bf... Merge branch 'master' of https://github.com/PiusLim373/CasinoArmServer
chain1 = ik.chain1

=======
>>>>>>> parent of d451ae9... after full run 1.0
=======
>>>>>>> parent of d451ae9... after full run 1.0
@app.route('/kek', methods = ['POST'])
def kekk():
	global ActivateArduino
	ActivateArduino = "YES"
	while True:
		print(ArduinoData)
		time.sleep(1)
	return 'uhoh'

@app.route('/initiate', methods=['POST'])
def InitiateGame():
	ActualGameProgress()
	return "0"

def CalculatePosition(distance, angle):
	array = [distance/2, angle/2, 0]
	return array

def Distribute1Card(coordinate, card):
	global test_i
<<<<<<< HEAD
<<<<<<< HEAD
	chain1.dispense()
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> parent of d451ae9... after full run 1.0
=======
>>>>>>> parent of d451ae9... after full run 1.0
=======
>>>>>>> parent of a9ac3bf... Merge branch 'master' of https://github.com/PiusLim373/CasinoArmServer
	CSx = CardStationPosition[0]
	CSy = CardStationPosition[1]
	CSz = CardStationPosition[2]
	x = coordinate[0]
	y = coordinate[1]
	z = coordinate[2]
	card.append(pakzan.readValue(test_i))
	ik.chain1_move_to(CSx, CSy, CSz)
	ik.pickupcard()
	ik.chain1_move_to(x, y ,z)
	ik.releasecard()
	test_i += 1
	return "0"

@app.route('/ArduinoDataHub', methods = ['POST', 'GET'])
def ArduinoDataHub():
	global ActivateArduino, ArduinoData
	if request.method == 'GET':
		return ActivateArduino
	else:
		data = request.get_json()
		ArduinoData = data['input']
		return "Input Captured"
		
def PromptforCard(coordinate, card):
		global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, ActivateArduino, ArduinoData
		ActivateArduino = "YES"
		while ArduinoData != "NO":
			if ArduinoData == "YES":
				if len(card) < 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font>'
					ArduinoData = ""
					ActivateArduino = "NO"
					Distribute1Card(coordinate, card)
					Jumbotron_text2 = "Do you wish to add more cards?"
					ActivateArduino = "YES"	
				elif len(card) == 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font><br><font color="red">This is the fifth and will the last card.</font>'
					ArduinoData = ""
					ActivateArduino = "NO"
					Distribute1Card(coordinate, card)
					return "0"
		Jumbotron_text2 = '<font color="red">You indicated that you don''t want anymore card, good luck :)</font>'
		ArduinoData = ""
		ActivateArduino = "NO"
		return "0"



def PromptforCardWithoutArduino(coordinate, card):
		global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, decision
		#wait for decision
		while decision == "":
			print("waiting...")
		while decision != 'NO' or decision == "":
			if decision == "YES":
				if len(card) < 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font>'
					Distribute1Card(coordinate, card)
					Jumbotron_text2 = "Do you wish to add more cards?"
					decision = "" 
				elif len(card) == 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font><br><font color="red">This is the fifth and will the last card.</font>'
					Distribute1Card(coordinate, card)
					decision = ""
					return "0"
		Jumbotron_text2 = '<font color="red">You indicated that you don''t want anymore card, good luck :)</font>'
		decision = ""
		return "0"

def CompileCardValue(card):
	SortedCard = collections.Counter(card)
	sumcase1 = 0
	sumcase2 = 0
	if SortedCard['A'] == 2:
		return 21
	else:
		sumcase1 = 10*SortedCard['K'] + 10*SortedCard['Q'] + 10*SortedCard['J'] + 10*SortedCard['10'] + 9*SortedCard['9'] + 8*SortedCard['8'] + 7*SortedCard['7'] + 6*SortedCard['6'] + 5*SortedCard['5'] + 4*SortedCard['4'] + 3*SortedCard['3'] + 2*SortedCard['2'] + 1*SortedCard['A']
		sumcase2 = 11*SortedCard['A'] + 10*SortedCard['K'] + 10*SortedCard['Q'] + 10*SortedCard['J'] + 10*SortedCard['10'] + 9*SortedCard['9'] + 8*SortedCard['8'] + 7*SortedCard['7'] + 6*SortedCard['6'] + 5*SortedCard['5'] + 4*SortedCard['4'] + 3*SortedCard['3'] + 2*SortedCard['2']
		if sumcase2 > sumcase1 and sumcase2 <= 21:
			return sumcase2
		else:
			return sumcase1
		
def ChecktoAddCard(coordinate, card, value):
	while value < 18:
		Distribute1Card(coordinate, card)
		value = CompileCardValue(card)
	return value

def OpenCardDeck(coordinate):
	x = coordinate[0]
	y = coordinate[1]
	z = coordinate[2]
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
	chain1.move_to(x, y, z)  #Move to deck's front
	chain1.move_to(x+10, y, z)  #Push deck until fall
=======
	chain1.move_to([x, y, z])  #Move to deck's front
	chain1.move_to([x+10, y, z])  #Push deck until fall
>>>>>>> 9193f838574d699465b1c568b9aa26472eae5554
=======
	ik.chain1_move_to(x, y, z)  #Move to deck's front
	ik.chain1_move_to(x+10, y, z)  #Push deck until fall
>>>>>>> parent of d451ae9... after full run 1.0
=======
	ik.chain1_move_to(x, y, z)  #Move to deck's front
	ik.chain1_move_to(x+10, y, z)  #Push deck until fall
>>>>>>> parent of d451ae9... after full run 1.0
=======
	chain1.move_to(x, y, z)  #Move to deck's front
	chain1.move_to(x+10, y, z)  #Push deck until fall
>>>>>>> parent of a9ac3bf... Merge branch 'master' of https://github.com/PiusLim373/CasinoArmServer
	return "0"


def EndGame(value1, value2, value3, value0):
	ValueArrAlias = ['Player 1', 'Player 2', 'Player 3', 'Dealer']
	ValueArr = [int(value1), int(value2), int(value3), int(value0)]
	Winner = []
	i = 0
	j = 0
	while i < len(ValueArr):
		if ValueArr[i] > 21:
			ValueArr[i] = 0
		i += 1 
	x = max(ValueArr) 
	if x != 0:
		while j < len(ValueArr):
			if ValueArr[j] == x:
				Winner.append(ValueArrAlias[j])
			j += 1
		return Winner
	else:
		return Winner	

@app.route('/')
def index():
	global test_i, Player1Position, Player2Position, Player3Position, Player1Card, Player2Card, Player3Card, Player1CardValue, Player2CardValue, Player3CardValue, ArmCard, ArmCardValue, ActivateArduino, ArduinoData
	Player1Position = []
	Player2Position = []
	Player3Position = []

	Player1Card = []
	Player2Card = []
	Player3Card = []

	Player1CardValue = 0
	Player2CardValue = 0
	Player3CardValue = 0

	ArmCard = []
	ArmCardValue = 0
	test_i = 0
	ActivateArduino = "NO"
	ArduinoData = ""
	return render_template('index.html')

@app.route('/StartGame', methods = ['POST'])
def StartGame():
	#Loads FaceRecog and get data output
	#r = subprocess.check_output('python FaceRecog\FaceRecog.py', shell = True)
	time.sleep(5)
	FaceRecog = subprocess.check_output('python Debug\debug.py 3 7', shell = True)          #Just a placeholder for debug
	FaceRecog_json = json.loads(FaceRecog)
	global Player1Position, Player2Position, Player3Position, ResetBtn
	ResetBtn = ""
	Player1Position = CalculatePosition(float(FaceRecog_json['players'][0]['position']['distance']), float(FaceRecog_json['players'][0]['position']['angle']))
	Player2Position = CalculatePosition(float(FaceRecog_json['players'][1]['position']['distance']), float(FaceRecog_json['players'][1]['position']['angle']))
	Player3Position = CalculatePosition(float(FaceRecog_json['players'][2]['position']['distance']), float(FaceRecog_json['players'][2]['position']['angle']))
	print(Player1Position)
	print(Player2Position)
	print(Player3Position)

	return "GameStarted.html"

@app.route('/GameStarted.html')
def GameStarted():

	return render_template("GameStarted.html")

@app.route('/admin')
def adminpage():
	return render_template("admin.html")

@app.route('/adminfeeds', methods = ['GET'])
def adminquery():
	return jsonify(CardStationPosition = [CardStationPosition], Jumbotron_title = Jumbotron_title, Jumbotron_text1 = Jumbotron_text1, Jumbotron_text2 = Jumbotron_text2, ArmPosition = [ArmPosition], ArmCard = [ArmCard], ArmCardValue = ArmCardValue, Player1Position = [Player1Position], Player1Card = [Player1Card], Player1CardValue = Player1CardValue, Player2Position = [Player2Position], Player2Card = [Player2Card], Player2CardValue = Player2CardValue, Player3Position = [Player3Position], Player3Card = [Player3Card], Player3CardValue = Player3CardValue)

@app.route('/feedback', methods = ['GET'])
def RealtimeFeedback():
	return jsonify(Jumbotron_title = Jumbotron_title, Jumbotron_text1 = Jumbotron_text1, Jumbotron_text2 = Jumbotron_text2, ResetBtn = ResetBtn)

@app.route('/ArduinoStimulation', methods = ['POST'])
def ArduinoStimulation():
	global decision
	decision = request.form['decision']
	print(decision)
	return ':)'

def ActualGameProgress():
	global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, ResetBtn
	#Distribute 1 card to each player, repeat 2 times
	Jumbotron_title = "Phase 1"
	Jumbotron_text1 = 'Distributing cards to all players. <font color = "red">Please be patient :)</font>'
	Jumbotron_text2 = "Distributing card to Player 1."
	Distribute1Card(Player1Position, Player1Card)
	Jumbotron_text2 = "Distributing card to Player 2."
	Distribute1Card(Player2Position, Player2Card)
	Jumbotron_text2 = "Distributing card to Player 3."
	Distribute1Card(Player3Position, Player3Card)
	Jumbotron_text2 = "Getting card for myself."
	Distribute1Card(ArmPosition, ArmCard)
	Jumbotron_text2 = "Distributing card to Player 1."
	Distribute1Card(Player1Position, Player1Card)
	Jumbotron_text2 = "Distributing card to Player 2."
	Distribute1Card(Player2Position, Player2Card)
	Jumbotron_text2 = "Distributing card to Player 3."
	Distribute1Card(Player3Position, Player3Card)
	Jumbotron_text2 = "Getting card for myself."
	Distribute1Card(ArmPosition, ArmCard)

	#Print out all cards in player's hand
	print(Player1Card)
	print(Player2Card)
	print(Player3Card)
	print(ArmCard)

	#Ask Players if want to add more card
	Jumbotron_title = "Phase 2"
	Jumbotron_text1 = 'Adding cards for <font color="red">Player 1</font>'
	Jumbotron_text2 = "Please indicate your choice with the device provided."
	PromptforCard(Player1Position, Player1Card)
	time.sleep(3)
	Jumbotron_text1 = 'Adding Cards for <font color="red">Player 2</font>'
	Jumbotron_text2 = "Please indicate your choice with the device provided."
	PromptforCard(Player2Position, Player2Card)
	time.sleep(3)
	Jumbotron_text1 = 'Adding Cards for <font color="red">Player 3</font>'
	Jumbotron_text2 = "Please indicate your choice with the device provided."
	PromptforCard(Player3Position, Player3Card)
	time.sleep(3)
	print(Player1Card)
	print(Player2Card)
	print(Player3Card)
	print(ArmCard)

	#Compile card value
	global Player1CardValue, Player2CardValue, Player3CardValue, ArmCardValue
	Player1CardValue = CompileCardValue(Player1Card)
	Player2CardValue = CompileCardValue(Player2Card)
	Player3CardValue = CompileCardValue(Player3Card)
	ArmCardValue = CompileCardValue(ArmCard)

	#decide whether to add more cards
	Jumbotron_text1 = "Adding cards for myself :p"
	Jumbotron_text2 = ""
	time.sleep(3)
	ChecktoAddCard(ArmPosition, ArmCard, ArmCardValue)

	#End Game, return a list of winners
	#announce everyone to open card
	Jumbotron_title = "Phase 3"
	Jumbotron_text1 = '<font color="red">Please flip over all your cards</font>'
	OpenCardDeck(ArmPosition)
	Winner = EndGame(Player1CardValue, Player2CardValue, Player3CardValue, ArmCardValue)
	time.sleep(5)
	i = 0
	Jumbotron_text2 = 'The game has ended.<br>Congratulation to <font color="red">'
	if len(Winner) == 1:
		Jumbotron_text2 += str(Winner[0])
		Jumbotron_text2 += "</font> to be the winner of the game!"
	else:
		while i < (len(Winner)-1):
			Jumbotron_text2 += str(Winner[i]) + ", "
			i += 1
		Jumbotron_text2 += "and " + str(Winner[i])
		Jumbotron_text2 += "</font> to be the winners of the game!" 
	ResetBtn = "show"
	




if __name__ == '__main__':
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
	app.run(host = "192.168.1.106", debug = True, use_reloader=False)
=======
	app.run(host = "192.168.1.103", debug = True, use_reloader=False)
>>>>>>> 9193f838574d699465b1c568b9aa26472eae5554
=======
	app.run(host = "192.168.1.106", debug = True)
>>>>>>> parent of d451ae9... after full run 1.0
=======
	app.run(host = "192.168.1.106", debug = True)
>>>>>>> parent of d451ae9... after full run 1.0
=======
	app.run(host = "192.168.1.106", debug = True, use_reloader=False)
>>>>>>> parent of a9ac3bf... Merge branch 'master' of https://github.com/PiusLim373/CasinoArmServer
