from flask import Flask, render_template, request, jsonify, Response
import requests
import time
import json
import os
import subprocess
from pprint import pprint
import serial
import collections
from Debug import pakzan, ik
#import ik
from multiprocessing import Process, Queue


app = Flask(__name__)

Player1Position = []
Player2Position = []
Player3Position = []

Player1Money = 100
Player2Money = 100
Player3Money = 100

Player1Bet = 0
Player2Bet = 0
Player3Bet = 0

#spade,love,diamond,club
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
BetPhase = ""
CurrPlayer = 0
CurrCard = []
ExistingPlayer = [1,1,1]

test_i = 0
decision = ""
ActivateArduino = ""
ArduinoDecision = ""
ArduinoBet = 0

chain1 = ik.chain1
#chain1 = ik.Kinematics(28,28,7,4)

#############################################PAKZAN CODE STARTS HERE
qFrame = Queue()
qStatus = Queue()
qPlayer = Queue()

@app.route('/FaceRecog')
def FaceRecog():
	return render_template("FaceRecog.html")

@app.route('/video_feed')
def video_feed():
	import FaceRecog
	# Run FaceRecog multiprocessor
	process = Process(target = FaceRecog.main, args = (qFrame, qStatus, qPlayer))
	process.start()

	def gen():
		while True:
			yield qFrame.get()
	
	# Get frame or player info from FaceRecog module
	# getFrameOrInfo function will keep yielding jpeg frame until all player information is found
	return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
	# Server Send Event for sending current status to frontend
	# status will then be converted to speech afterwards
	def gen():
		while True:
			yield 'data: {}\n\n'.format(qStatus.get())
	return Response(gen(), mimetype='text/event-stream')

@app.route('/player_info')
def player_info():
    # FaceRecog.getFrameOrInfo() will return values after all players' faces found for 2 seconds
    # player_info = {'Player 1': [location(cm), angle(degree)], 'Player 2': ...}
    # format: DICTIONARY = {STRING: [float, float]}
    def gen():
        while True:
            yield 'data: {}\n\n'.format(qPlayer.get())
    return Response(gen(), mimetype='text/event-stream')

#############################################PAKZAN CODE ENDS HERE


@app.route('/ReceivePlayerInfo', methods = ['POST'])
def ReceivePlayerInfo():
	global Player1Position, Player2Position, Player3Position, ResetBtn
	ResetBtn = ""
	try:
		Player1Position = request.form['Player 1'].split()
		Player1Position = [float(i) for i in Player1Position]
		Player1Position.append(0)
		Player2Position = request.form['Player 2'].split()
		Player2Position = [float(i) for i in Player2Position]
		Player2Position.append(0)
		Player3Position = request.form['Player 3'].split()
		Player3Position = [float(i) for i in Player3Position]
		Player3Position.append(0)

	except Exception as e:
		pass
	print(request.form)
	print(Player1Position)
	print(Player2Position)
	print(Player3Position)
	return "Player position registered"


@app.route('/kek', methods = ['POST'])
def kekk():
	Distribute1Card([1,2,3], Player1Card)
	return 'uhoh'

@app.route('/initiate', methods=['POST'])
def InitiateGame():
	ActualGameProgress()
	return "0"

@app.route('/card_info', methods = ['POST'])
def info():
	global rank, suit
	rank = request.form['rank']
	suit = request.form['suit']
	print([rank, suit])
	return ""


def Distribute1Card(coordinate, card):
	global test_i
	chain1.dispense()
	card.append([rank, suit])
	chain1.move_to(CardStationPosition)
	chain1.grip(1)
	chain1.move_to(coordinate)
	chain1.grip(0)
	print(Player1Card)
	test_i += 1
	return "0"

@app.route('/ArduinoDataHub', methods = ['POST', 'GET'])
def ArduinoDataHub():
	global ActivateArduino, ArduinoDecision, ArduinoBet
	if request.method == 'GET':
		return ActivateArduino
	else:
		data = request.get_json()
		ArduinoBet = data['bet'] 
		ArduinoDecision = data['decision']
		print(ArduinoBet)
		print(ArduinoDecision)
		return "Input Captured"
		
def PromptforBet(x, money):
	global ArduinoBet, ActivateArduino, ArduinoDecision, Jumbotron_text1, Jumbotron_text2, Player1Bet, Player2Bet, Player3Bet, Player1Money, Player2Money, Player3Money, ExistingPlayer
	ActivateArduino = "BET"
	while ArduinoDecision != "PLACEBET":
		Jumbotron_text1 = '<font color="red">Player ' + str(x) +'</font> is placing bets.'
		Jumbotron_text2 = "Please response with the device provided :)<br>You have S$" + str(money) + "."
		if ArduinoBet != "":
			if x == 1:
				Player1Bet = round(int(ArduinoBet)/100 * money)
				bet = Player1Bet
				if bet == 0:
					# print("Player 1 opted out.")
					ExistingPlayer[0] = 0
				else:
					ExistingPlayer[0] = 1
			elif x == 2:
				Player2Bet = round(int(ArduinoBet)/100 * money)
				bet = Player2Bet
				if bet == 0:
					#print("Player 2 opted out.")
					ExistingPlayer[1] = 0
				else:
					ExistingPlayer[1] = 1
			elif x == 3:
				Player3Bet = round(int(ArduinoBet)/100 * money)
				bet = Player3Bet
				if bet == 0:
					#print("Player 3 opted out.")
					ExistingPlayer[2] = 0
				else:
					ExistingPlayer[2] = 1
	ArduinoDecision = ""
	ActivateArduino = "DECISION"
	if bet == 0:
		Jumbotron_text2 = '<font color="red">You are about opt out from the game. Are you sure?</font>'
	else: 
		Jumbotron_text2 = '<font color="red">You are about to place S$' + str(bet) +". Are you sure?</font>"
	while ArduinoDecision == "":
		if ArduinoDecision == "NO":
			ActivateArduino = ""
			ArduinoDecision = ""
			PromptforBet(x, money)
		elif ArduinoDecision == "YES":
			if x == 1:
					Player1Money -= Player1Bet
					money = Player1Money
			elif x == 2:
					Player2Money -= Player2Bet
					money = Player2Money
			elif x == 3:
					Player3Money -= Player3Bet
					money = Player3Money
			if bet == 0:
				Jumbotron_text2 = '<font color="red">Player ' + str(x) + " has opted out from the game. </font>"
			else: 
				Jumbotron_text2 = '<font color="green">Bet placed, you have S$' + str(money) + " remaining. Good Luck!</font>"
			ActivateArduino = ""
			ArduinoBet = 0
			ArduinoDecision = ""
			time.sleep(3)
			return 0
	


	

def PromptforCard(coordinate, card):
		global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, ActivateArduino, ArduinoDecision
		ActivateArduino = "YES"
		while ArduinoDecision != "NO":
			if ArduinoDecision == "YES":
				if len(card) < 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font>'
					ArduinoDecision = ""
					ActivateArduino = "NO"
					Distribute1Card(coordinate, card)
					Jumbotron_text2 = "Do you wish to add more cards?"
					ActivateArduino = "YES"	
				elif len(card) == 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font><br><font color="red">This is the fifth and will the last card.</font>'
					ArduinoDecision = ""
					ActivateArduino = "NO"
					Distribute1Card(coordinate, card)
					return "0"
		Jumbotron_text2 = '<font color="red">You indicated that you don''t want anymore card, good luck :)</font>'
		ArduinoDecision = ""
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
	coordinate_push = []
	for x in coordinate:
		coordinate_push.append(x)
	coordinate_push[0] += 10
	chain1.move_to(coordinate)  #Move to deck's front
	chain1.move_to(coordinate_push)  #Push deck until fall
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
	global test_i, Player1Position, Player2Position, Player3Position, Player1Card, Player2Card, Player3Card, Player1CardValue, Player2CardValue, Player3CardValue, ArmCard, ArmCardValue, ActivateArduino, ArduinoDecision
	'''Player1Position = []
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
				ArduinoDecision = ""
			
				ExistingPlayer = [1,1,1]'''
	return render_template('index.html')


@app.route('/GameStarted.html')
def GameStarted():

	return render_template("GameStarted.html")

@app.route('/admin')
def adminpage():
	return render_template("admin.html")

@app.route('/adminfeeds', methods = ['GET'])
def adminquery():
	return jsonify(CardStationPosition = [CardStationPosition], Jumbotron_title = Jumbotron_title, Jumbotron_text1 = Jumbotron_text1, Jumbotron_text2 = Jumbotron_text2, ArmPosition = [ArmPosition], ArmCard = [ArmCard], ArmCardValue = ArmCardValue, Player1Position = [Player1Position], Player1Card = [str(Player1Card)], Player1CardValue = Player1CardValue, Player1Money = Player1Money, Player1Bet = Player1Bet, Player2Position = [Player2Position], Player2Card = [Player2Card], Player2CardValue = Player2CardValue, Player2Money = Player2Money, Player2Bet = Player2Bet, Player3Position = [Player3Position], Player3Card = [Player3Card], Player3CardValue = Player3CardValue, Player3Money = Player3Money, Player3Bet = Player3Bet)

@app.route('/feedback', methods = ['GET'])
def RealtimeFeedback():
	return jsonify(Jumbotron_title = Jumbotron_title, Jumbotron_text1 = Jumbotron_text1, Jumbotron_text2 = Jumbotron_text2, ResetBtn = ResetBtn, Player1Bet = Player1Bet,Player2Bet = Player2Bet, Player3Bet = Player3Bet, CurrPlayer = CurrPlayer, ArduinoBet = ArduinoBet, BetPhase = BetPhase, Player1Money = Player1Money)

@app.route('/ArduinoStimulation', methods = ['POST'])
def ArduinoStimulation():
	global decision
	decision = request.form['decision']
	print(decision)
	return ':)'

def ActualGameProgress():
	global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, ResetBtn, BetPhase, CurrPlayer
	#Distribute 1 card to each player, repeat 2 times
	BetPhase = "show"
	Jumbotron_title = "Phase 1: Bet Placing"
	CurrPlayer = 1
	PromptforBet(1, Player1Money)
	CurrPlayer = 2
	PromptforBet(2, Player2Money)
	CurrPlayer = 3
	PromptforBet(3, Player3Money)
	CurrPlayer = 0
	BetPhase = ""
	print(Player1Bet)
	print(Player2Bet)
	print(Player3Bet)


	Jumbotron_text1 = 'Distributing cards to all players. <font color = "red">Please be patient :)</font>'
	if ExistingPlayer[0] == 1:
		Jumbotron_text2 = "Distributing card to Player 1."
		Distribute1Card(Player1Position, Player1Card)
	if ExistingPlayer[1] == 1:	
		Jumbotron_text2 = "Distributing card to Player 2."
		Distribute1Card(Player2Position, Player2Card)
	if ExistingPlayer[2] == 1:
		Jumbotron_text2 = "Distributing card to Player 3."
		Distribute1Card(Player3Position, Player3Card)
	Jumbotron_text2 = "Getting card for myself :p"
	Distribute1Card(ArmPosition, ArmCard)
	if ExistingPlayer[0] == 1:
		Jumbotron_text2 = "Distributing card to Player 1."
		Distribute1Card(Player1Position, Player1Card)
	if ExistingPlayer[1] == 1:
		Jumbotron_text2 = "Distributing card to Player 2."
		Distribute1Card(Player2Position, Player2Card)
	if ExistingPlayer[2] == 1:
		Jumbotron_text2 = "Distributing card to Player 3."
		Distribute1Card(Player3Position, Player3Card)
	Jumbotron_text2 = "Getting card for myself :p"
	Distribute1Card(ArmPosition, ArmCard)

	#Print out all cards in player's hand
	print(Player1Card)
	print(Player2Card)
	print(Player3Card)
	print(ArmCard)

	#Ask Players if want to add more card
	Jumbotron_title = "Phase 2"
	if ExistingPlayer[0] == 1:
		Jumbotron_text1 = 'Adding cards for <font color="red">Player 1</font>'
		Jumbotron_text2 = "Please indicate your choice with the device provided."
		PromptforCardWithoutArduino(Player1Position, Player1Card)
		time.sleep(3)
	if ExistingPlayer[1] == 1:
		Jumbotron_text1 = 'Adding Cards for <font color="red">Player 2</font>'
		Jumbotron_text2 = "Please indicate your choice with the device provided."
		PromptforCardWithoutArduino(Player2Position, Player2Card)
		time.sleep(3)
	if ExistingPlayer[2] == 1:
		Jumbotron_text1 = 'Adding Cards for <font color="red">Player 3</font>'
		Jumbotron_text2 = "Please indicate your choice with the device provided."
		PromptforCardWithoutArduino(Player3Position, Player3Card)
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
	app.run(host = "0.0.0.0", debug = True)