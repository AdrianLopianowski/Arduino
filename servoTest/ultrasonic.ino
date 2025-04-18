#define trigPin 12
#define echoPin 11
#include <Servo.h>

Servo myServo;

int servoPin = 9;

bool working = false;
int pozycjaServo = 0;
int liczba = 1;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  myServo.attach(servoPin);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "start") {
      working = true;
    } else if (command == "stop") {
      working = false;
    }
  }

  if (working) {
    long czas, dystans;

    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    czas = pulseIn(echoPin, HIGH);
    dystans = czas / 58;

    Serial.print(dystans);
    Serial.println(" cm");

    myServo.write(pozycjaServo);
    delay(50);

    if (pozycjaServo == 180) {
      liczba = -1;
    } else if (pozycjaServo == 0) {
      liczba = 1;
    }

    pozycjaServo += liczba;
  }
}
