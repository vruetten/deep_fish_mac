const int pump= 10; //LED connected to digital pin 10
const int LEDpump= 11; //LED connected to digital pin 10v

const int pumpTime = 500;

void setup()
{
pinMode(pump, OUTPUT); //sets the digital pin as output
pinMode(LEDpump, OUTPUT); //sets the digital pin as output
}

void loop()
{
digitalWrite(pump,HIGH); //turns the LED on
digitalWrite(LEDpump,HIGH); //turns the LED onv
delay(1000);
digitalWrite(pump,LOW);
digitalWrite(LEDpump,LOW);
delay(4000);
}

