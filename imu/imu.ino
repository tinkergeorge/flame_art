#include <Adafruit_BNO08x.h>

#define BNO08X_RESET -1

Adafruit_BNO08x bno08x(BNO08X_RESET);
sh2_SensorValue_t bnoSensorValue;

void setup(void)
{
  Serial.begin(115200);
  while (!Serial)
    delay(10);

  Serial.println("Light Curve IMU");

  if (!bno08x.begin_I2C())
  {
    Serial.println("Failed to find BNO08x chip");
    while (1)
    {
      delay(10);
    }
  }

  Serial.println("BNO08x Found!");

  for (int n = 0; n < bno08x.prodIds.numEntries; n++)
  {
    Serial.print("Part ");
    Serial.print(bno08x.prodIds.entry[n].swPartNumber);
    Serial.print(": Version :");
    Serial.print(bno08x.prodIds.entry[n].swVersionMajor);
    Serial.print(".");
    Serial.print(bno08x.prodIds.entry[n].swVersionMinor);
    Serial.print(".");
    Serial.print(bno08x.prodIds.entry[n].swVersionPatch);
    Serial.print(" Build ");
    Serial.println(bno08x.prodIds.entry[n].swBuildNumber);
  }

  tellBnoWhatReportsWeWant();

  Serial.println("Reading events");
  delay(100);
}

void tellBnoWhatReportsWeWant(void)
{
  Serial.println("Setting desired reports");
  if (!bno08x.enableReport(SH2_GAME_ROTATION_VECTOR))
  {
    Serial.println("Could not enable game vector");
  }
}

void loop()
{
  delay(10);

  if (bno08x.wasReset())
  {
    Serial.print("Sensor was reset - ");
    tellBnoWhatReportsWeWant();
  }

  if (!bno08x.getSensorEvent(&bnoSensorValue))
  {
    return;
  }

  switch (bnoSensorValue.sensorId)
  {
  case SH2_GAME_ROTATION_VECTOR:
    Serial.print("Game Rotation Vector - r: ");
    Serial.print(bnoSensorValue.un.gameRotationVector.real);
    Serial.print(" i: ");
    Serial.print(bnoSensorValue.un.gameRotationVector.i);
    Serial.print(" j: ");
    Serial.print(bnoSensorValue.un.gameRotationVector.j);
    Serial.print(" k: ");
    Serial.println(bnoSensorValue.un.gameRotationVector.k);
    break;
  }
}