import pyttsx3
engine = pyttsx3.init()
x = 1
BetRate = 2
Player3Bet = 50
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)
engine.say('Dealer has won the bet!'+ str(Player3Bet)+ '$ of bet placed earlier has been credited to the dealer, dont be sad.')
engine.runAndWait()