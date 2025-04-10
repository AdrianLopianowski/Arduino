#include <Servo.h>

Servo myServo;         
int servoPin = 9;     //pin

void setup() {
  Serial.begin(9600);          
  myServo.attach(servoPin);   
}

void loop() {
  if (Serial.available() > 0) {
    int angle = Serial.parseInt();  
    
    
    if (angle >= 0 && angle <= 180) {
      myServo.write(angle);         
      Serial.print("Ustawiono kąt: ");
      Serial.println(angle);
    }
  }
}
