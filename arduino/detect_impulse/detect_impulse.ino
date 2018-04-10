


const int constLED = 9;
const int pump = 10; //LED connected to digital pin 10
const int LEDpump = 11; //LED connected to digital pin 10


int on_time = 1;
int off_time = 1;
int analogValue = 0;
char inByte;

void setup() {
  Serial.begin(9600); // set the baud rate - 960 characters arrive per second 
  Serial.println("Ready"); // print "Ready" once
  pinMode(constLED, OUTPUT); //sets the digital pin as output
  pinMode(pump, OUTPUT); //sets the digital pin as output
  pinMode(LEDpump, OUTPUT); //sets the digital pin as output
}

void loop() {
  if(Serial.available()){ // only send data back if data has been sent
    inByte = Serial.read(); // read the incoming data
    //delay(2);s
    Serial.print("received from PC: ");
    Serial.println(inByte);
  }

    if (inByte=='r'){
     off_time = 10;
     on_time = 1;
      }
      
   if (inByte=='u'){
     on_time = on_time+1;
      }
     
      
   if (inByte=='d'){
     on_time = on_time-1;
     if (on_time<0){
        on_time = 0;
     }
      }

    // increase off time
    if (inByte=='k'){
     off_time = off_time+1;
      }

    // decrease off time
    if (inByte=='j'){
     off_time = off_time-1;
      if (off_time<0){
        off_time = 0;
     }
      }
                
    if (inByte=='1'){
      Serial.println("1 detected ");
      //digitalWrite(LEDpump,HIGH); //turns the LED onv
        if (off_time ==0){
        }
        else{
          digitalWrite(pump,HIGH); //turns the LED on
          delay(on_time);
          digitalWrite(pump,LOW); //turns the LED on
          delay(off_time);
        }
    }
    
     if (inByte=='0'){
      Serial.println("0 detected ");
      digitalWrite(pump,LOW); //turns the LED on
      digitalWrite(LEDpump,LOW); //turns the LED onv
    } 
    digitalWrite(constLED,HIGH);  
    
}
