void setup() {
Serial.begin(9600); // set the baud rate
Serial.println("Ready"); // print "Ready" once
}
void loop() {
char inByte;
if(Serial.available()){ // only send data back if data has been sent
  //inByte =  Serial.readStringUntil('\n'); // read the incoming data
  inByte =  Serial.read();
  // read the input on analog pin 0:
  // int sensorValue = analogRead(A0);
  // print out the value you read:
  Serial.println(inByte);
}
delay(200); // delay for 1/10 of a second
}
