

int on_time = 500;
int off_time;
int analogValue = 0;

const int pump= 10; //LED connected to digital pin 10
const int LEDpump= 11; //LED connected to digital pin 10v


void setup() 
{
  Serial.begin(9600); // set the baud rate
  // 960 characters arrive per second 
  Serial.println("Ready"); // print "Ready" once
  pinMode(pump, OUTPUT); //sets the digital pin as output
  pinMode(LEDpump, OUTPUT); //sets the digital pin as output
}

void loop() {
  if(Serial.available()){ // only send data back if data has been sent
    
    int inByte = Serial.read(); // read the incoming data
    Serial.print("received from PC: ");
    Serial.println(inByte);
    delay(100);
    analogValue ++;
    if (analogValue>255){
      analogValue = 0;
    }
    Serial.print("ard sent: ");
    Serial.println(analogValue, DEC);  // print as an ASCII-encoded decimal
    delay(100);
    }
  digitalWrite(pump,HIGH); //turns the LED on
  digitalWrite(LEDpump,HIGH); //turns the LED onv
  delay(1000);
  digitalWrite(pump,LOW);
  digitalWrite(LEDpump,LOW);
  delay(1000);
//    delay(50);
//    Serial.print(inByte);
    
    //Serial.println("hello");
//  delay(100); // delay for 1/10 of a second
}
