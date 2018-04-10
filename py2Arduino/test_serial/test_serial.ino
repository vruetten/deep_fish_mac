

int on_time = 500;
int off_time;
int analogValue = 0;

const int pump= 10; //LED connected to digital pin 10
const int LEDpump= 11; //LED connected to digital pin 10
int pumpTime = 500;

String readString = "";

void setup() 
{
  Serial.begin(9600); // set the baud rate
  // 960 characters arrive per second 
  Serial.println("Ready"); // print "Ready" once
  
  pinMode(pump, OUTPUT); //sets the digital pin as output
  pinMode(LEDpump, OUTPUT); //sets the digital pin as output
}


void loop() {
  while (Serial.available()) {
    char c = Serial.read();  //gets one byte from serial buffer
    readString += c; //makes the string readString
    delay(2);  //slow looping to allow buffer to fill with next character
    Serial.print("readString is:");
    Serial.println(readString);  //so you can see the captured string 
   
  }

  if (readString.length() >0) {
    Serial.print("integer is:");
    pumpTime = readString.toInt();  //convert readString into a number
    Serial.println(pumpTime);  //so you can see the captured string 
  }
  digitalWrite(pump,HIGH); //turns the LED on
  digitalWrite(LEDpump,HIGH); //turns the LED onv
  delay(pumpTime);
  digitalWrite(pump,LOW);
  digitalWrite(LEDpump,LOW);
  delay(4000);

  readString=""; //empty for next input

}
  
