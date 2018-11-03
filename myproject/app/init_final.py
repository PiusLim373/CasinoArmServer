from flask import Flask, render_template, request, jsonify, Response
import requests
import time
import json
import os
import subprocess
from pprint import pprint
import serial
import collections
#from Debug import pakzan, ik
from arm_pos import ik
from multiprocessing import Process, Queue
import logging
# import pyttsx3

app = Flask(__name__)

# engine = pyttsx3.init()
# engine.setProperty('rate', rate-50)
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

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

ArmPosition = [0,40,0]   #This is position of Arm's Card deck
ArmCard = []
ArmCardValue = 0
ArmMoney = 0

Jumbotron_title = ""
Jumbotron_text1 = ""
Jumbotron_text2 = ""
ResetBtn = ""
BetPhase = ""
CurrPlayer = 0
CurrCard = []
ExistingPlayer = [0,0,0]

test_i = 0
decision = ""
ActivateArduino = ""
ArduinoDecision = ""
ArduinoBet = 0
rank = ""

#chain1 = ik.chain1

###Debug mode
# debug mode
# Player1Position = [32.6,44.3,23.9]
# Player2Position = [12.6,22.8,30.8]
# Player3Position = [11.5,8,22.6, 2]
# ExistingPlayer = [1,1,1]

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
		i = 1
		while True:
			speech = qStatus.get()
			print (speech)
			time.sleep(0.1)
			yield 'data: {}\n\n'.format(speech)
	return Response(gen(), mimetype='text/event-stream')

@app.route('/player_info')
def player_info():
	# FaceRecog.getFrameOrInfo() will return values after all players' faces found for 2 seconds
	# player_info = {'Player 1': [location(cm), angle(degree)], 'Player 2': ...}
	# format: DICTIONARY = {STRING: [float, float]}
	def gen():
		while True:
			PlayerInfo = qPlayer.get()
			ReceivePlayerInfo(PlayerInfo)
			yield 'data: {}\n\n'.format(PlayerInfo)
	return Response(gen(), mimetype='text/event-stream')

def ReceivePlayerInfo(PlayerInfo):
	PlayerList = []
	for key, value in PlayerInfo.items():
		PlayerList.append(value)
	PlayerList.sort(reverse=True, key=lambda x: x[1])

	global Player1Position, Player2Position, Player3Position, ResetBtn, ExistingPlayer
	ResetBtn = ""
	try:
		Player1Position = PlayerList[0]
		Player1Position.append(0)
		ExistingPlayer[0] = 1
		Player2Position = PlayerList[1]
		Player2Position.append(0)
		ExistingPlayer[1] = 1
		Player3Position = PlayerList[2]
		Player3Position.append(0)
		ExistingPlayer[2] = 1

	except Exception as e:
		pass
	print("from main:" + str(Player1Position))
	print("from main:" + str(Player2Position))
	print("from main:" + str(Player3Position))
	return "Player position registered"


#############################################PAKZAN CODE ENDS HERE

#############################################MINGJI CODE STARTS HERE

def get_result(player_hand, dealer_hand):
	player_score = CompileCardValue(player_hand)
	dealer_score = CompileCardValue(dealer_hand)

	if player_score > 21 and dealer_score <= 21:
		return 'dealer'

	if player_score > 21 and dealer_score > 21:
		return 'draw'

	if player_score <= 21 and dealer_score > 21:
		return 'player'

	if len(player_hand) < 5 and len(dealer_hand) < 5 and player_score > dealer_score:
		return 'player'

	if len(player_hand) < 5 and len(dealer_hand) < 5 and player_score < dealer_score:
		return 'dealer'

	if len(player_hand) == 5 and len(dealer_hand) < 5:
		if player_score <= 21 and dealer_score != 21:
			return 'player'
		if player_score <= 21 and dealer_score == 21:
			return 'draw'

	if len(dealer_hand) == 5 and len(player_hand) < 5:
		if dealer_score <= 21 and player_score != 21:
			return 'player'
		if dealer_score <= 21 and player_score == 21:
			return 'draw'

	if len(dealer_hand) == 5 and len(player_hand) == 5:
		if dealer_score <= 21 and player_score > 21:
			return 'dealer'
		if dealer_score > 21 and player_score <= 21:
			return 'player'
		if dealer_score <= 21 and player_score <= 21:
			return 'draw'

	return 'draw'

def get_bet_rate(hand):
	score = CompileCardValue(hand)
	ace_count = hand.count('1')
	jack_count = hand.count('11')
	queen_count = hand.count('12')
	king_count = hand.count('13')

	if len(hand) < 5 and score < 21:
		return 1

	if len(hand) == 2 and ace_count == 2:
		return 3

	if len(hand) == 2 and ace_count == 1 or jack_count == 1 or queen_count == 1 or king_count == 1:
		return 2

	if len(hand) == 5 and score < 21:
		return 2

	if len(hand) < 5 and score == 21:
		return 2

	if len(hand) == 5 and score == 21:
		return 3

	

###########################################################MINGJI CODES END HERE

@app.route('/kek', methods = ['POST'])
def kekk():
	Distribute1Card([1,2,3], Player1Card)
	return ''

@app.route('/initiate', methods=['POST'])
def InitiateGame():
	ActualGameProgress()
	return "0"

@app.route('/card_info', methods = ['POST'])
def info():
	global rank
	rank = request.form['rank']
	print(rank)
	return ""


def Distribute1Card(coordinate, card):
	global test_i, rank
	chain1.dispense()
	rank = ""
	while rank == "":
		pass
	card.append(rank)
	# card.append(pakzan.readValue(test_i))
	chain1.dynamixel_write(CardStationPosition)
	chain1.grip(1)
	chain1.dynamixel_write(CardStationStandbyPosition)
	chain1.move_to(coordinate)
	chain1.grip(0)
	print(Player1Card)
	test_i += 1
	chain1.dynamixel_write(CardStationStandbyPosition)
	return "0"

@app.route('/ArduinoDataHub', methods = ['POST', 'GET'])
def ArduinoDataHub():
	global ActivateArduino, ArduinoDecision, ArduinoBet
	if request.method == 'GET':
		return ActivateArduino
	else:
		data = request.get_json()
		ArduinoBet = data['bet'] if data['bet'] != '' else ArduinoBet
		ArduinoDecision = data['decision']
		print(ArduinoBet)
		print(ArduinoDecision)
		return "Input Captured"
		
def PromptforBet(x, money):
	global ArduinoBet, ActivateArduino, ArduinoDecision, Jumbotron_text1, Jumbotron_text2, Player1Bet, Player2Bet, Player3Bet, Player1Money, Player2Money, Player3Money, ExistingPlayer
	ActivateArduino = "BET"
	while ArduinoDecision != "PLACEBET":
		Jumbotron_text1 = '<font color="red">Player ' + str(x) +'</font> is placing bets.'
		Jumbotron_text2 = "Please respond with the device provided :)<br>You have S$" + str(money) + "."
		# engine.say('Player' + str(x) + 'is placing bets, Please response with the device provided.')
		# engine.runAndWait()
		if ArduinoBet != "":
			## Remake

			## Remake ends

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
	while True:
		if ArduinoDecision == "NO":
			ActivateArduino = ""
			ArduinoDecision = ""
			return PromptforBet(x, money)
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
	
def PromptforBetRemake(x, money):
	global ArduinoBet, ActivateArduino, ArduinoDecision, Jumbotron_text1, Jumbotron_text2, Player1Bet, Player2Bet, Player3Bet, Player1Money, Player2Money, Player3Money, ExistingPlayer
	ActivateArduino = "BET"
	while ArduinoDecision != "PLACEBET":
		Jumbotron_text1 = '<font color="red">Player ' + str(x) +'</font> is placing bets.'
		Jumbotron_text2 = "Please respond with the device provided :)<br>You have S$" + str(money) + "."
		if ArduinoBet != "":
			bet = round(int(ArduinoBet)/100 * money)
	ArduinoDecision = ""
	ActivateArduino = "DECISION"
	if bet == 0:
		Jumbotron_text2 = '<font color="red">You are about opt out from the game. Are you sure?</font>'
	else: 
		Jumbotron_text2 = '<font color="red">You are about to place S$' + str(bet) +". Are you sure?</font>"
	while True:
		if ArduinoDecision == "NO":
			ActivateArduino = ""
			ArduinoDecision = ""
			return PromptforBetRemake(x, money)
		elif ArduinoDecision == "YES":
			if bet != 0:
				if x == 1:
					Player1Bet = bet
					Player1Money -= Player1Bet
					money = Player1Money
				elif x == 2:
					Player2Bet = bet
					Player2Money -= Player2Bet
					money = Player2Money
				elif x == 3:
					Player3Bet = bet
					Player3Money -= Player3Bet
					money = Player3Money
				Jumbotron_text2 = '<font color="green">Bet placed, you have S$' + str(money) + " remaining. Good Luck!</font>"
			elif bet == 0:
				Jumbotron_text2 = '<font color="red">Player ' + str(x) + " has opted out from the game. </font>"
				if x == 1: 
					ExistingPlayer[0] = 0
				elif x == 2:
					ExistingPlayer[1] = 0
				elif x == 3:
					ExistingPlayer[2] = 0
				
			ActivateArduino = ""
			ArduinoBet = 0
			ArduinoDecision = ""
			time.sleep(3)
			return 0

	

def PromptforCard(coordinate, card):
		global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, ActivateArduino, ArduinoDecision
		ActivateArduino = "DECISION"
		while ArduinoDecision != "NO":
			if ArduinoDecision == "YES":
				if len(card) < 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font>'
					ArduinoDecision = ""
					ActivateArduino = ""
					Distribute1Card(coordinate, card)
					Jumbotron_text2 = "Do you wish to add more cards?"
					ActivateArduino = "DECISION"	
				elif len(card) == 4:
					Jumbotron_text2 = '<font color="green">You indicated that you want to add 1 more card, just a sec ;)</font><br><font color="red">This is the fifth and will the last card.</font>'
					ArduinoDecision = ""
					ActivateArduino = ""
					Distribute1Card(coordinate, card)
					return "0"
		Jumbotron_text2 = '<font color="red">You indicated that you don''t want anymore card, good luck :)</font>'
		ArduinoDecision = ""
		ActivateArduino = ""
		return "0"



def PromptforCardWithoutArduino(coordinate, card):
		global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, decision
		#wait for decision
		while decision == "":
			pass
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
	if SortedCard['1'] == 2:
		return 21
	else:
		sumcase1 = 10*SortedCard['13'] + 10*SortedCard['12'] + 10*SortedCard['11'] + 10*SortedCard['10'] + 9*SortedCard['9'] + 8*SortedCard['8'] + 7*SortedCard['7'] + 6*SortedCard['6'] + 5*SortedCard['5'] + 4*SortedCard['4'] + 3*SortedCard['3'] + 2*SortedCard['2'] + 1*SortedCard['1']
		sumcase2 = 11*SortedCard['1'] + 10*SortedCard['13'] + 10*SortedCard['12'] + 10*SortedCard['11'] + 10*SortedCard['10'] + 9*SortedCard['9'] + 8*SortedCard['8'] + 7*SortedCard['7'] + 6*SortedCard['6'] + 5*SortedCard['5'] + 4*SortedCard['4'] + 3*SortedCard['3'] + 2*SortedCard['2']
		if sumcase2 > sumcase1 and sumcase2 <= 21:
			return sumcase2
		else:
			return sumcase1
		
def ChecktoAddCard(coordinate, card, value):
	while value < 17:
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

def WaitforButtonPress():
	global ActivateArduino, ArduinoDecision
	ActivateArduino = "DECISION"
	while ArduinoDecision != "YES":
		pass
	ArduinoDecision = ""
	ActivateArduino = ""
	return 0

def WaitforButtonPressWithoutArduino():
	global decision
	while decision != "YES":
		pass
	decision = ""
	return 0

@app.route('/')
def index():
	global test_i, Player1Position, Player2Position, Player3Position, Player1Card, Player2Card, Player3Card, Player1CardValue, Player2CardValue, Player3CardValue, Player1Money, Player2Money, Player3Money, Player1Bet, Player2Bet, Player3Bet, ArmCard, ArmCardValue, ArmMoney, ResetBtn, ActivateArduino, ArduinoDecision, ExistingPlayer, ArduinoBet, decision, rank
	Player1Position = []
	Player2Position = []
	Player3Position = []

	Player1Card = []
	Player2Card = []
	Player3Card = []

	Player1Money = 100
	Player2Money = 100
	Player3Money = 100

	Player1CardValue = 0
	Player2CardValue = 0
	Player3CardValue = 0

	Player1Bet = 0
	Player2Bet = 0
	Player3Bet = 0

	ArmCard = []
	ArmCardValue = 0
	ArmMoney = 0

	ResetBtn = ""
	ExistingPlayer = [0,0,0]

	test_i = 0
	decision = ""
	ActivateArduino = ""
	ArduinoDecision = ""
	ArduinoBet = 0
	rank = ""
	return render_template('index.html')


@app.route('/GameStarted.html')
def GameStarted():

	return render_template("GameStarted.html")

@app.route('/admin')
def adminpage():
	return render_template("admin.html")

@app.route('/adminfeeds', methods = ['GET'])
def adminquery():
	return jsonify(CardStationPosition = [CardStationPosition], Jumbotron_title = Jumbotron_title, Jumbotron_text1 = Jumbotron_text1, Jumbotron_text2 = Jumbotron_text2, ArmPosition = [ArmPosition], ArmCard = [ArmCard], ArmCardValue = ArmCardValue, Player1Position = [Player1Position], Player1Card = [Player1Card], Player1CardValue = Player1CardValue, Player1Money = Player1Money, Player1Bet = Player1Bet, Player2Position = [Player2Position], Player2Card = [Player2Card], Player2CardValue = Player2CardValue, Player2Money = Player2Money, Player2Bet = Player2Bet, Player3Position = [Player3Position], Player3Card = [Player3Card], Player3CardValue = Player3CardValue, Player3Money = Player3Money, Player3Bet = Player3Bet)

@app.route('/feedback', methods = ['GET'])
def RealtimeFeedback():
	return jsonify(Jumbotron_title = Jumbotron_title, Jumbotron_text1 = Jumbotron_text1, Jumbotron_text2 = Jumbotron_text2, ResetBtn = ResetBtn, Player1Bet = Player1Bet,Player2Bet = Player2Bet, Player3Bet = Player3Bet, CurrPlayer = CurrPlayer, ArduinoBet = ArduinoBet, BetPhase = BetPhase, Player1Money = Player1Money, Player2Money = Player2Money, Player3Money = Player3Money, ExistingPlayer1 = ExistingPlayer[0], ExistingPlayer2 = ExistingPlayer[1], ExistingPlayer3 = ExistingPlayer[2])

@app.route('/ArduinoStimulation', methods = ['POST'])
def ArduinoStimulation():
	global decision
	decision = request.form['decision']
	print(decision)
	return ':)'

@app.route('/RestartWithoutReset', methods = ['POST'])
def RestartWithoutReset():
	global Player1Bet, Player2Bet, Player3Bet, Player1Card, Player2Card, Player3Card, Player1CardValue, Player2CardValue, Player3CardValue, ArmCard, ArmCardValue, decision, ActivateArduino, ArduinoDecision, ArduinoBet, rank, ResetBtn
	Player1Bet = 0
	Player2Bet = 0
	Player3Bet = 0

	Player1Card = []
	Player2Card = []
	Player3Card = []

	Player1CardValue = 0
	Player2CardValue = 0
	Player3CardValue = 0

	ArmCard = []
	ArmCardValue = 0

	decision = ""
	ActivateArduino = ""
	ArduinoDecision = ""
	ArduinoBet = 0
	rank = ""
	ResetBtn = ""

	return '/GameStarted.html'

def ActualGameProgress():
	global Player1Money, Player2Money, Player3Money, ArmMoney, Player1Bet, Player2Bet, Player3Bet
	global Jumbotron_title, Jumbotron_text1, Jumbotron_text2, ResetBtn, BetPhase, CurrPlayer
	# # Distribute 1 card to each player, repeat 2 times
	#chain1.dynamixel_write(CardStationStandbyPosition)
	BetPhase = "show"
	Jumbotron_title = "Phase 1: Placing of Bets"
	if ExistingPlayer[0] == 1:
		CurrPlayer = 1
		PromptforBetRemake(1, Player1Money)
	if ExistingPlayer[1] == 1:
		CurrPlayer = 2
		PromptforBetRemake(2, Player2Money)
	if ExistingPlayer[2] == 1:
		CurrPlayer = 3
		PromptforBetRemake(3, Player3Money)
	CurrPlayer = 0
	BetPhase = ""
	print(Player1Bet)
	print(Player2Bet)
	print(Player3Bet)

	# Player1Bet = 50
	# Player2Bet = 60
	# Player3Bet = 100
	# Player1Money -= Player1Bet
	# Player2Money -= Player2Bet
	# Player3Money -= Player3Bet

	Jumbotron_title = "Phase 2: Distribution of Card"
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
	#chain1.dynamixel_write(CardStationStandbyPosition)
	#Ask Players if want to add more card
	Jumbotron_title = "Phase 3: Card Adding"
	if ExistingPlayer[0] == 1:
		Jumbotron_text1 = 'Adding cards for <font color="red">Player 1</font>'
		Jumbotron_text2 = "Please indicate your choice with the device provided."
		PromptforCard(Player1Position, Player1Card)
		#chain1.dynamixel_write(CardStationStandbyPosition)
		time.sleep(1)
	if ExistingPlayer[1] == 1:
		Jumbotron_text1 = 'Adding Cards for <font color="red">Player 2</font>'
		Jumbotron_text2 = "Please indicate your choice with the device provided."
		PromptforCard(Player2Position, Player2Card)
		#chain1.dynamixel_write(CardStationStandbyPosition)
		time.sleep(1)
	if ExistingPlayer[2] == 1:
		Jumbotron_text1 = 'Adding Cards for <font color="red">Player 3</font>'
		Jumbotron_text2 = "Please indicate your choice with the device provided."
		PromptforCard(Player3Position, Player3Card)
		time.sleep(1)
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
	time.sleep(1)
	ArmCardValue = ChecktoAddCard(ArmPosition, ArmCard, ArmCardValue)
	#chain1.dynamixel_write(CardStationStandbyPosition)

	#End Game, return a list of winners
	#announce everyone to open card
	Jumbotron_title = "Phase 4: Dealer vs. Players"
	Jumbotron_text1 = 'All players will compare your cards with the dealer.'
	OpenCardDeck(ArmPosition)
	time.sleep(3)
	if (ExistingPlayer[0] == 1):
		Jumbotron_text1 = '<font color="red">Player 1 please open your cards.</font>'
		Jumbotron_text2 = "Very complicated calculation process is happening in the background..."
		chain1.move_to(Player1Position)
		Winner = get_result(Player1Card, ArmCard)
		if Winner == "player":
			BetRate = get_bet_rate(Player1Card)
			print(BetRate)
			Jumbotron_text1 = '<font color="green">Player 1 has won with odds of ' + str(BetRate) + " to 1 </font>"
			Player1Money += ((1 + BetRate) * Player1Bet)
			Jumbotron_text2 = "S$" + str(Player1Bet * BetRate) + " has been credited to Player 1, Congratulations!<br>Press Button 1 to continue."
			WaitforButtonPress()
			Player1Bet = 0
		elif Winner == "dealer":
			BetRate = get_bet_rate(ArmCard)
			Jumbotron_text1 = '<font color="red">Player 1 had lost.</font>'
			Jumbotron_text2 = "S$" + str(Player1Bet) +" of bet placed earlier will be credited to the dealer.<br>Press Button 1 to continue."
			ArmMoney += Player1Bet
			WaitforButtonPress()
			Player1Bet = 0
		elif Winner == "draw":
			Jumbotron_text1 = "It's a draw!"
			Jumbotron_text2 = "No money will be collected from player, S$" + str(Player1Bet) + " has been credited back to Player 1.<br>Press Button 1 to continue."
			Player1Money += Player1Bet
			WaitforButtonPress()
			Player1Bet = 0
		#chain1.dynamixel_write(CardStationStandbyPosition)

	if (ExistingPlayer[1] == 1):
		Jumbotron_text1 = '<font color="red">Player 2 please open your cards.</font>'
		Jumbotron_text2 = "Very complicated calculation process is happening in the background..."
		chain1.move_to(Player2Position)
		Winner = get_result(Player2Card, ArmCard)
		if Winner == "player":
			BetRate = get_bet_rate(Player2Card)
			print(BetRate)
			Jumbotron_text1 = '<font color="green">Player 2 has won with odds of ' + str(BetRate) + " to 1 </font>"
			Player2Money += ((1 + BetRate) * Player2Bet)
			Jumbotron_text2 = "S$" + str(Player2Bet * BetRate) + " has been credited to Player 2, Congratulations!<br>Press Button 1 to continue."
			WaitforButtonPress()
			Player2Bet = 0
		elif Winner == "dealer":
			BetRate = get_bet_rate(ArmCard)
			Jumbotron_text1 = '<font color="red">Player 2 had lost.</font>'
			Jumbotron_text2 = "S$" + str(Player2Bet) +" of bet placed earlier will be credited to the dealer.<br>Press Button 1 to continue."
			ArmMoney += Player2Bet
			WaitforButtonPress()
			Player2Bet = 0
		elif Winner == "draw":
			Jumbotron_text1 = "It's a draw!"
			Jumbotron_text2 = "No money will be collected from player, S$" + str(Player2Bet) + " has been credited back to Player 2.<br>Press Button 1 to continue."
			Player2Money += Player2Bet
			WaitforButtonPress()
			Player2Bet = 0
		
		#chain1.dynamixel_write(CardStationStandbyPosition)


	if (ExistingPlayer[2] == 1):
		Jumbotron_text1 = '<font color="red">Player 3 please open your cards.</font>'
		Jumbotron_text2 = "Very complicated calculation process is happening in the background..."
		chain1.move_to(Player3Position)
		Winner = get_result(Player3Card, ArmCard)
		if Winner == "player":
			BetRate = get_bet_rate(Player3Card)
			print(BetRate)
			Jumbotron_text1 = '<font color="green">Player 3 has won with odds of ' + str(BetRate) + " to 1 </font>"
			Player3Money += ((1 + BetRate) * Player3Bet)
			Jumbotron_text2 = "S$" + str(Player3Bet * BetRate) + " has been credited to Player 3, Congratulations!<br>Press Button 1 to continue."
			WaitforButtonPress()
			Player3Bet = 0
		elif Winner == "dealer":
			BetRate = get_bet_rate(ArmCard)
			Jumbotron_text1 = '<font color="red">Player 3 had lost.</font>'
			Jumbotron_text2 = "S$" + str(Player3Bet) +" of bet placed earlier will be credited to the dealer.<br>Press Button 1 to continue."
			ArmMoney += Player3Bet
			WaitforButtonPress()
			Player3Bet = 0
		elif Winner == "draw":
			Jumbotron_text1 = "It's a draw!"
			Jumbotron_text2 = "No money will be collected from player, S$" + str(Player3Bet) + " has been credited back to Player 3.<br>Press Button 1 to continue."
			Player3Money += Player3Bet
			WaitforButtonPress()
			Player3Bet = 0
	chain1.dynamixel_write(CardStationStandbyPosition)
	Jumbotron_title = "The End"
	Jumbotron_text1 = "The game has ended, thank you for your participation"
	Jumbotron_text2 = 'Press the <font color="green">CONTINUE</font> button to play 1 more round, or the <font color="red">RESET</font> button to start a <b>new</b> game.'
	ResetBtn = "show"
	




if __name__ == '__main__':
	global chain1
	chain1 = ik.Kinematics(11,12,8,7)
	global CardStationStandbyPosition,CardStationPosition
	deck = chain1.deck
	deck1 = chain1.deck1
	CardStationStandbyPosition = deck1
	CardStationPosition = deck
	app.run(host = "192.168.1.101", debug = True, use_reloader = False)
