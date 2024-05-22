int enA = 9;
int in1 = 4;
int in2 = 5;
int enB = 10;
int in3 = 6;
int in4 = 7;

int servoGrip = 13;

int move;

bool ballStatus = false;

const int trigPin = 11;
const int echoPin = 12;

void setup() {
  pinMode(enA, OUTPUT);
  pinMode(enB, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);

  Serial.begin(9600);
}

void loop() {
  if (ballStatus) {
    Serial.println("Shooting");
  } else if (checkDistance() <= 5) {
    gripBall();
  } else {
    move = checkSerial();
    if (move == 0) {
      moveStraight();
    } else if (move == 1) {
      moveLeft();
    } else if (move == 2) {
      moveRight();
    } else if (move == 3) {
      rotate();
    }
  }
  // delay(500);
}

void gripBall() {
  Serial.println(servoGrip);
}

int checkSerial() {
  if (Serial.available() > 0) {
    String receivedDataString = Serial.readStringUntil('\n');
    int receivedData = receivedDataString.toInt();

    Serial.print("Received: ");
    Serial.println(receivedData);
    return receivedData;
  }
  return 6;
}

int checkDistance() {
  long duration, distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration * 0.034) / 2;  

  Serial.print("Distance: ");
  Serial.println(distance);
  return distance;
}

void moveStraight() {
  analogWrite(enA, 100);
  analogWrite(enB, 100);

  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  delay(50);
  stopMotors();
}

void moveLeft() {
  analogWrite(enA, 100);
  analogWrite(enB, 100);

  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  delay(50);
  stopMotors();
}

void moveRight() {
  analogWrite(enA, 100);
  analogWrite(enB, 100);

  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  delay(50);
  stopMotors();
}

void rotate() {
  moveLeft();
  moveRight();
  delay(50);
  stopMotors();
}

void stopMotors() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}
