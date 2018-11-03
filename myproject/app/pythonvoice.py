import pyttsx3
engine = pyttsx3.init()
x = 1
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)
# engine.say('Player' + str(x) + 'is placing bets, Please response with the device provided.')
engine.say('hi yiu kang')
engine.runAndWait()