
// read and write

int on_time;
int off_time;

void setup() 
{
  Serial.begin(9600); // set the baud rate
  Serial.println("Ready"); // print "Ready" once
}


void loop() {
//  while(Serial.available()){
//    char c = Serial.read() //gets one byte from serial buffer
//  }

  char inByte = 'h';
  float something = millis()/10000.0;
  int value = int(100+ 50 * sin( something * 2.0 * PI  ));
//  if(Serial.available()){ // only send data back if data has been sent
//    char inByte = Serial.read(); // read the incoming data
//    Serial.println(inByte); // send the data back in a new line so that it is not all one long line
    Serial.println(something);
//  }
  delay(1000); // delay for 1/10 of a second
}


