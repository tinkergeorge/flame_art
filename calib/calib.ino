#include <Adafruit_PWMServoDriver.h>


const int NUM_VALVES = 3;
float valveStates[NUM_VALVES];  // Stores valve states (0.0 to 1.0)
int calMin[NUM_VALVES];  // Stores min calibration values (microseconds)
int calMax[NUM_VALVES];  // Stores max calibration values (microseconds)

struct ValveData {
  float currentValue;
  float nextValue;
  unsigned long previousTime;
  unsigned long nextTime;
};

ValveData valveData[NUM_VALVES];
bool artMode = false;

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

void setup() {
  Serial.begin(115200);
  delay(1000);
  pwm.begin();
  Serial.println("pwm begun");
  pwm.setOscillatorFrequency(25200000);
  pwm.setPWMFreq(50);  // Analog servos run at ~50 Hz updates

  for (int i = 0; i < NUM_VALVES; i++) {
    valveStates[i] = 0.0;
    calMin[i] = 500;  // Default values
    calMax[i] = 2500;  // Default values
  }
  Serial.println("Valve Controller Interface");
  Serial.println("Type commands and press enter to execute.");
  Serial.print("> ");  // Command line symbol
}

void loop() {
  if (artMode) {
    updateArtMode();
    delay(30);  // Add a delay to throttle the output rate
  }

  static String commandBuffer;  // Holds the incoming command
  while (Serial.available() > 0) {
    char inChar = Serial.read();  // Read a character
    if (inChar == '\n') {  // Check for the end of the command
      processCommand(commandBuffer);  // Process the complete command
      commandBuffer = "";  // Clear the command buffer
      Serial.print("> ");  // Display the command line symbol again
    } else {
      commandBuffer += inChar;  // Add the character to the command buffer
    }
  }
}


void setValveState(int valveNum, float state) {
  valveStates[valveNum] = state;
  int servoValue = calMin[valveNum] + (calMax[valveNum] - calMin[valveNum]) * state;
  controlValve(valveNum, servoValue);
  Serial.print("Set valve ");
  Serial.print(valveNum + 1);
  Serial.print(" to state ");
  Serial.println(state);
}


void displayValves() {
  Serial.println();
  for (int i = 0; i < NUM_VALVES; i++) {
    Serial.print("Valve ");
    Serial.print(i + 1);
    Serial.print(": |");
    int position = (int)(valveStates[i] * 16);  // Assuming a scale of 10
    for (int j = 0; j < 16; j++) {
      if (j == position) {
        Serial.print("X");
      } else {
        Serial.print("-");
      }
    }
    Serial.print("| Cal: (");
    Serial.print(calMin[i]);
    Serial.print(", ");
    Serial.print(calMax[i]);
    Serial.print(") Val: ");
    Serial.println(valveStates[i], 1);  // 1 decimal place precision
  }
}

void testValve(int valveNum) {
  float testPositions[3] = {0.0, 0.5, 1.0};
  for (int j = 0; j < 3; j++) {
    setValveState(valveNum, testPositions[j]);
    delay(1000);
  }
  setValveState(valveNum, 0.0);  // Reset to 0 after testing
}

void rangeTest() {
  for (int i = 0; i < NUM_VALVES; i++) {
    testValve(i);
  }
  Serial.println("Range test completed");
}

void setCalibration(int valveNum, int minVal, int maxVal) {
  calMin[valveNum] = minVal;
  calMax[valveNum] = maxVal;
  Serial.print("Calibrated valve ");
  Serial.print(valveNum + 1);
  Serial.print(" with min ");
  Serial.print(minVal);
  Serial.print(" and max ");
  Serial.println(maxVal);
  testValve(valveNum);  // Test the specified valve after calibration
}

void setupArtMode() {
  for (int i = 0; i < NUM_VALVES; i++) {
    valveData[i].currentValue = 0.0;
    valveData[i].nextValue = random(0, 100) / 100.0;
    valveData[i].previousTime = millis();
    valveData[i].nextTime = millis() + random(1000, 5000);  // Random time between 1 to 5 seconds
  }
  artMode = true;
}

void updateArtMode() {
  unsigned long currentTime = millis();
  for (int i = 0; i < NUM_VALVES; i++) {
    if (currentTime >= valveData[i].nextTime) {
      // Update data for next interpolation cycle
      valveData[i].previousTime = valveData[i].nextTime;
      valveData[i].nextTime = currentTime + random(1000, 5000);
      valveData[i].currentValue = valveData[i].nextValue;
      valveData[i].nextValue = random(0, 100) / 100.0;
    }
    // Interpolate valve position
    float t = (float)(currentTime - valveData[i].previousTime) / (valveData[i].nextTime - valveData[i].previousTime);
    float interpolatedValue = lerp(valveData[i].currentValue, valveData[i].nextValue, t);
    setValveState(i, interpolatedValue);
  }
  displayStateMachineStatus();
  displayValves();
}

void displayStateMachineStatus() {
  Serial.print("Art Mode Active | Time: ");
  Serial.print(millis());
  Serial.println(" ms");
}

float lerp(float a, float b, float t) {
  return a + t * (b - a);
}

void processCommand(String command) {
  char cmdType = command.charAt(0);
  artMode = false;  // Exit art mode if active
  
  if (cmdType == 'd') {
    displayValves();
    return;
  } else if (cmdType == 'r') {
    rangeTest();
    return;
  } else if (cmdType == 'a') {
    setupArtMode();
    return;
  }
  
  int valveNum = command.charAt(1) - '0';
  if (valveNum < 1 || valveNum > NUM_VALVES) {
    Serial.println("Invalid valve number");
    return;
  }
  valveNum -= 1;  // Adjust to 0-indexed

  int spaceIndex = command.indexOf(' ');
  if (spaceIndex == -1) {
    Serial.println("Unrecognized command");
    return;
  }

  if (cmdType == 'v') {
    float valveState = command.substring(spaceIndex + 1).toFloat();
    setValveState(valveNum, valveState);
  } else if (cmdType == 'c') {
    int secondSpaceIndex = command.indexOf(' ', spaceIndex + 1);
    if (secondSpaceIndex == -1) {
      Serial.println("Unrecognized command");
      return;
    }
    int minVal = command.substring(spaceIndex + 1, secondSpaceIndex).toInt();
    int maxVal = command.substring(secondSpaceIndex + 1).toInt();
    setCalibration(valveNum, minVal, maxVal);
  } else {
    Serial.println("Unrecognized command");
  }
}


void controlValve(int valveNum, int servoValue) {
  pwm.writeMicroseconds(valveNum, servoValue);
}
