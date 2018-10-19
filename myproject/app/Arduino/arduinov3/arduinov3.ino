#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
char* ssid = "TP-LINK_B1027A";
char* password = "64959900";

void setup() {

  Serial.begin(9600);
  WiFi.begin(ssid, password);

  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println("Waiting for connections...");
  }
  Serial.println("Wifi Connected!");
}

void loop() {
  if(WiFi.status()== WL_CONNECTED){   //Check WiFi connection status
   StaticJsonBuffer<300> JSONbuffer;
   JsonObject& JSONencoder = JSONbuffer.createObject(); 
   JSONencoder["input"] = "YES";
   char JSONmessageBuffer[300];
    JSONencoder.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
    Serial.println(JSONmessageBuffer);
   HTTPClient http;    //Declare object of class HTTPClient
 
   http.begin("http://192.168.1.105:5000/ArduinoInput");      //Specify request destination
   http.addHeader("Content-Type", "application/json");  //Specify content-type header
 
   int httpCode = http.POST(JSONmessageBuffer);   //Send the request
   String payload = http.getString();                  //Get the response payload
 
   Serial.println(httpCode);   //Print HTTP return code
   Serial.println(payload);    //Print request response payload
 
   http.end();  //Close connection
 
   }
   else{
 
    Serial.println("Error in WiFi connection");   
 
   }
 
  delay(3000); 
}
