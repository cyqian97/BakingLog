String  incomingByte; // for incoming serial data

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  Serial.setTimeout(100);
}

void loop() {
  // reply only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.readStringUntil('\r');

    // say what you got:
    Serial.print("I received: ");
    Serial.println(incomingByte.toInt());
  }
}
