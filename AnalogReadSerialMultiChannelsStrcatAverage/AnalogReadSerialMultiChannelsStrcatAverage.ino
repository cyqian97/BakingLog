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
  analogReadResolution(12);
  String result = "";
  int channelNum = 6;
  float averageNum = 100.0;
  int sensorValues[] = {0,0,0,0,0,0};
  for (int j = 0; j < averageNum; j = j + 1) {
    for (int i = 0; i < channelNum; i = i + 1) {
      sensorValues[i] = sensorValues[i] + analogRead(i);
      delay(1); 
    }
  }
  
  for (int i = 0; i < channelNum; i = i + 1) {
    result = result + float(sensorValues[i])/averageNum;
    result = result + "\t";
  }
  Serial.println(result);
  delay(1);      // delay in between reads for stability
}

// the loop routine runs over and over again forever:
void loop() {
  String result = "";
  int channelNum = 6;
  float averageNum = 250.0;
  int sensorValues[] = {0,0,0,0,0,0};
  for (int j = 0; j < averageNum; j = j + 1) {
    for (int i = 0; i < channelNum; i = i + 1) {
      sensorValues[i] = sensorValues[i] + analogRead(i);
      delay(1); 
    }
  }
  
  for (int i = 0; i < channelNum; i = i + 1) {
    result = result + float(sensorValues[i])/averageNum;
    result = result + "\t";
  }
  Serial.println(result);
  delay(1);      // delay in between reads for stability
}
