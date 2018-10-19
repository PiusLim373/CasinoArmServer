#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
char* ssid = "TP-LINK_B1027A";
char* password = "64959900";
const int yesbuttonPin = 5;   
const int nobuttonPin = 4;
const int ledPin = 13;     
const int yesled = 2;
const int noled = 0;

int ledState = HIGH;       
int yesbuttonState;            
int nobuttonState;
int lastyesButtonState = LOW;  
int lastnoButtonState = LOW;

unsigned long lastyesDebounceTime = 0;  
unsigned long lastnoDebounceTime = 0;
unsigned long debounceDelay = 50;    

void setup() {
  pinMode(yesbuttonPin, INPUT);
  pinMode(nobuttonPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(yesled, OUTPUT);
  pinMode(noled,OUTPUT);
  digitalWrite(ledPin, ledState);
  digitalWrite(yesled, LOW);
  digitalWrite(noled,LOW);
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println("Waiting for connections...");
  }
  Serial.println("Wifi Connected!");
}

void loop() {
  HTTPClient http;   
  http.begin("http://192.168.1.106:5000/ArduinoDataHub");    
  http.addHeader("Content-Type", "application/json");  
  StaticJsonBuffer<300> JSONbuffer;
  JsonObject& JSONencoder = JSONbuffer.createObject();
  int httpGetCode = http.GET();
  String GetPayload = http.getString();
  Serial.println(GetPayload);
  while (GetPayload == "YES"){
    //Serial.println("Waiting for button press");
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
          ledState = !ledState;
          digitalWrite(yesled,HIGH);
          JSONencoder["input"] = "YES";
          char JSONmessageBuffer[300];
          JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
          Serial.println(JSONmessageBuffer);
          int httpCode = http.POST(JSONmessageBuffer);
          Serial.println(httpCode);
          http.end();
          delay(1000);
          digitalWrite(yesled,LOW);
        
  
        }
      }
    }
    if ((millis() - lastnoDebounceTime) > debounceDelay){
      if(noreading != nobuttonState){
        nobuttonState = noreading;
        if(nobuttonState == HIGH){
          unsigned long LastMillis = millis();
          ledState = !ledState;
          digitalWrite(noled,HIGH);
          unsigned long CurrentMillis = millis();
          JSONencoder["input"] = "NO";
          char JSONmessageBuffer[300];
          JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
          Serial.println(JSONmessageBuffer);
          int httpCode = http.POST(JSONmessageBuffer);
          Serial.println(httpCode);
          http.end();
          delay(1000);
          digitalWrite(noled,LOW);
          
        }
      }  
    }
  
    digitalWrite(ledPin, ledState);
    lastyesButtonState = yesreading;
    lastnoButtonState = noreading;
    httpGetCode = http.GET();
    GetPayload = http.getString();
    delay(50);
    }
    delay(300);
  
}
