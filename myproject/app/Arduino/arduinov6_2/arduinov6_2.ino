#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
char* ssid = "DevourerOP";
char* password = "123456789";
const int yesbuttonPin = 5;   
const int nobuttonPin = 4;
const int ledPin = 13;     
const int yesled = 2;
const int noled = 0;

int yesbuttonState;            
int nobuttonState;
int lastyesButtonState = LOW;  
int lastnoButtonState = LOW;

unsigned long lastyesDebounceTime = 0;  
unsigned long lastnoDebounceTime = 0;
unsigned long debounceDelay = 10;    
HTTPClient http; 

void setup() {
  pinMode(yesbuttonPin, INPUT);
  pinMode(nobuttonPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(yesled, OUTPUT);
  pinMode(noled,OUTPUT);
  pinMode(A0,INPUT);
  digitalWrite(yesled, LOW);
  digitalWrite(noled,LOW);
  digitalWrite(ledPin,HIGH);
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println("Waiting for connections...");
  }
  Serial.println("Wifi Connected!");
    
   
}


int SendDecisionJSON(String input){
  http.begin("http://192.168.1.101:5000/ArduinoDataHub");    
  http.addHeader("Content-Type", "application/json");
  StaticJsonBuffer<300> JSONbuffer;
  JsonObject& JSONencoder = JSONbuffer.createObject();
  JSONencoder["bet"] = "";
  JSONencoder["decision"] = input;
  char JSONmessageBuffer[300];
  JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  Serial.println(JSONmessageBuffer);
  int httpCode = http.POST(JSONmessageBuffer);
  Serial.println(httpCode);
  http.end();
  return 0;
}

int SendBetJSON(int input){
  http.begin("http://192.168.1.101:5000/ArduinoDataHub");    
  http.addHeader("Content-Type", "application/json");
  StaticJsonBuffer<300> JSONbuffer;
  JsonObject& JSONencoder = JSONbuffer.createObject();
  JSONencoder["bet"] = input;
  JSONencoder["decision"] = "";
  char JSONmessageBuffer[300];
  JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
  int httpCode = http.POST(JSONmessageBuffer);
  http.end();
  return 0;
}
void DecisionLoop(){
    int yesreading = digitalRead(yesbuttonPin);
    int noreading = digitalRead(nobuttonPin);

    if (yesreading != lastyesButtonState) {
      lastyesDebounceTime = millis();
    }
    else if(noreading != lastnoButtonState){
      lastnoDebounceTime= millis();
    }
    
    if ((millis() - lastyesDebounceTime) > debounceDelay) {
      if (yesreading != yesbuttonState) {
        yesbuttonState = yesreading;
        if (yesbuttonState == HIGH) {
          digitalWrite(yesled,HIGH);
          SendDecisionJSON("YES");
          delay(1000);
          digitalWrite(yesled,LOW);
        
  
        }
      }
    }
    if ((millis() - lastnoDebounceTime) > debounceDelay){
      if(noreading != nobuttonState){
        nobuttonState = noreading;
        if(nobuttonState == HIGH){
          digitalWrite(noled,HIGH);
          SendDecisionJSON("NO");
          delay(1000);
          digitalWrite(noled,LOW);
          
        }
      }  
    }
    lastyesButtonState = yesreading;
    lastnoButtonState = noreading;
}

int prevBet = 0;
int BetLoop(){
    int PotMeter = analogRead(A0);
    int yesreading = digitalRead(yesbuttonPin);
    int bet = map(PotMeter, 0, 1023, 0, 100);
    if (abs(prevBet - bet) >= 1 ){
      SendBetJSON(bet);
      prevBet = bet;
    }
    if (yesreading != lastyesButtonState) {
      lastyesDebounceTime = millis();
    }
    if ((millis() - lastyesDebounceTime) > debounceDelay) {
      if (yesreading != yesbuttonState) {
        yesbuttonState = yesreading;
        if (yesbuttonState == HIGH) {
          digitalWrite(yesled,HIGH);
          SendDecisionJSON("PLACEBET");
          delay(1000);
          digitalWrite(yesled,LOW);
        }
      }
    }
    lastyesButtonState = yesreading;
    return 0;
}
///////////////////////////////////////////////////////////////////// MAINLOOP
void loop() { 
  http.begin("http://192.168.1.101:5000/ArduinoDataHub");    
  http.addHeader("Content-Type", "application/json"); 
  int httpGetCode = http.GET();
  String GetPayload = http.getString();
  http.end();
  if(GetPayload == "BET"){
    while(GetPayload == "BET"){
      Serial.println("BET");
      digitalWrite(ledPin, LOW);
      BetLoop();
      delay(10);
      http.begin("http://192.168.1.101:5000/ArduinoDataHub");    
      http.addHeader("Content-Type", "application/json"); 
      int httpGetCode = http.GET();
      GetPayload = http.getString();
      http.end();
    }
  }
  
  else if(GetPayload == "DECISION"){
    while(GetPayload == "DECISION"){
      
      digitalWrite(ledPin, LOW);
      DecisionLoop();
      delay(10);
      http.begin("http://192.168.1.101:5000/ArduinoDataHub");    
      http.addHeader("Content-Type", "application/json"); 
      int httpGetCode = http.GET();
      GetPayload = http.getString();
      http.end();
    }
  }

  else digitalWrite(ledPin, HIGH);
  delay(100);
  
}
