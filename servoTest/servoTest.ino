#include <Servo.h>

Servo myServo;         
int servoPin = 9;      

void setup() {
  myServo.attach(servoPin); 
}

void loop() {
  
  for (int angle = 0; angle <= 180; angle++) {
    myServo.write(angle);  
    delay(15);             
  }


  for (int angle = 180; angle >= 0; angle--) {
    myServo.write(angle);
    delay(15);
  }
}
