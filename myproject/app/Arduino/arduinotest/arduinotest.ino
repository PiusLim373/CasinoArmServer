
void setup() {
  // put your setup code here, to run once:
  pinMode(0, OUTPUT);
  pinMode(2,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(2,HIGH);
  Serial.println("pin4 HIGH");
  delay(100);
  digitalWrite(2, LOW);
  Serial.println("pin4 LOW");
  delay(100);
  digitalWrite(0,HIGH);
  Serial.println("pin3 HIGH");
  delay(100);
  digitalWrite(0, LOW);
  Serial.println("pin3 LOW");
  delay(100);
}
