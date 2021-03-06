/*
  AnalogReadSerial

  Reads an analog input on pin 0, prints the result to the Serial Monitor.
  Graphical representation is available using Serial Plotter (Tools > Serial Plotter menu).
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/AnalogReadSerial
*/

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  Serial.println("ready");
}

// the loop routine runs over and over again forever:
void loop() {
  int sensorValue = 0;
  int channelNum = 6;
  
  for (int i = 0; i < channelNum; i = i + 1) {
    sensorValue = analogRead(i);
    Serial.print(sensorValue);
    Serial.print("\t");
  }
  Serial.println("");

  delay(1000);      // delay in between reads for stability
}
