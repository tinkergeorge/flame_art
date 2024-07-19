#include <Adafruit_BNO08x.h>

#include <SPI.h>
#include <WiFi101.h>
#include <WiFiUdp.h>

// From "OSC" library in Arduino. You can find it by searching for "Open Sound Control" in library manager.
#include <OSCMessage.h>

#define BNO08X_RESET -1

IPAddress ip(192, 168, 13, 211);
IPAddress gateway(192, 168, 13, 1);
IPAddress subnet(255, 255, 255, 0);

Adafruit_BNO08x bno08x(BNO08X_RESET);
sh2_SensorValue_t bnoSensorValue;

int status = WL_IDLE_STATUS;

// Create a secrets file with your network info that looks like:
// #define IMU_SSID "my ssid"
// #define IMU_PASS "password"
// #include "imu_secrets.h"
// char SSID[] = IMU_SSID;
// char PASS[] = IMU_PASS;
char SSID[] = "lightcurve";
char PASS[] = "curvelight";

WiFiUDP udp;

void setup(void)
{
  Serial.begin(115200);
  // while (!Serial)
  delay(200);

  Serial.println("Light Curve IMU");

  WiFi.setPins(8, 7, 4, 2);
  if (WiFi.status() == WL_NO_SHIELD)
  {
    Serial.println("WiFi shield not detected. This means something is wrong with the code or you are running this on a different board. Goodbye.");
    while (true)
    {
      delay(10);
    }
  }

  int checkCount = 0;
  while (WiFi.status() != WL_CONNECTED)
  {
    if (checkCount <= 0)
    {
      Serial.print("Trying to connect to SSID: ");
      Serial.println(SSID);

      WiFi.begin(SSID, PASS);
      WiFi.config(ip, gateway, subnet);
      checkCount = 25;
    }

    delay(400);
    checkCount--;
  }
  Serial.println("Connected to wifi");
  printWiFiStatus();

  if (!bno08x.begin_I2C())
  {
    Serial.println("Failed to find BNO08x chip");
    while (true)
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

  udp.begin(6510);

  Serial.println("Reading events");
  delay(100);
}

void printWiFiStatus()
{
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void tellBnoWhatReportsWeWant(void)
{
  Serial.println("Setting desired reports");
  if (!bno08x.enableReport(SH2_GRAVITY))
  {
    Serial.println("Could not enable gravity report");
  }
  if (!bno08x.enableReport(SH2_GAME_ROTATION_VECTOR))
  {
    Serial.println("Could not enable game rotation report");
  }
}

void loop()
{
  delay(100);

  if (bno08x.wasReset())
  {
    Serial.print("Sensor was reset - ");
    tellBnoWhatReportsWeWant();
  }

  if (!bno08x.getSensorEvent(&bnoSensorValue))
  {
    return;
  }

  IPAddress targetIpAddress(192, 168, 13, 255);
  switch (bnoSensorValue.sensorId)
  {
  case SH2_GRAVITY:
  {
    Serial.print("Gravity - x: ");
    Serial.print(bnoSensorValue.un.gravity.x);
    Serial.print(" y: ");
    Serial.print(bnoSensorValue.un.gravity.y);
    Serial.print(" z: ");
    Serial.println(bnoSensorValue.un.gravity.z);

    OSCMessage msg("/LC/gravity");

    msg.add(bnoSensorValue.un.gravity.x);
    msg.add(bnoSensorValue.un.gravity.y);
    msg.add(bnoSensorValue.un.gravity.z);

    udp.beginPacket(targetIpAddress, 6511);
    msg.send(udp);
    udp.endPacket();
    udp.beginPacket(targetIpAddress, 6512);
    msg.send(udp);
    udp.endPacket();
  }
  break;
  case SH2_GAME_ROTATION_VECTOR:
  {
    Serial.print("Game Rotation Vector - r: ");
    Serial.print(bnoSensorValue.un.gameRotationVector.real);
    Serial.print(" i: ");
    Serial.print(bnoSensorValue.un.gameRotationVector.i);
    Serial.print(" j: ");
    Serial.print(bnoSensorValue.un.gameRotationVector.j);
    Serial.print(" k: ");
    Serial.println(bnoSensorValue.un.gameRotationVector.k);

    OSCMessage msg("/LC/rotation");

    msg.add(bnoSensorValue.un.gameRotationVector.i);
    msg.add(bnoSensorValue.un.gameRotationVector.j);
    msg.add(bnoSensorValue.un.gameRotationVector.k);

    udp.beginPacket(targetIpAddress, 6511);
    msg.send(udp);
    udp.endPacket();
    udp.beginPacket(targetIpAddress, 6512);
    msg.send(udp);
    udp.endPacket();
  }
  break;
  }
}
