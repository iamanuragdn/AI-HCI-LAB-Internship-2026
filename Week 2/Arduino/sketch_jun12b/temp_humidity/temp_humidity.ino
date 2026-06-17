#include "DHT.h"

// We plugged the Data wire into Digital Pin 2
#define DHTPIN 2     

// Tell the code which sensor you bought
#define DHTTYPE DHT22   

// Set up the sensor
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Start the communication to your computer screen
  Serial.begin(9600);
  Serial.println(F("DHT22 sensor is waking up..."));

  // Start the sensor
  dht.begin();
}

void loop() {
  // The DHT22 is a bit slow, so we wait 2 seconds between readings
  delay(2000);

  // Read humidity and raw temperature
  float h = dht.readHumidity();
  float rawTemp = dht.readTemperature(); // Reads in Celsius

  // Check if the reading failed
  if (isnan(h) || isnan(rawTemp)) {
    Serial.println(F("Failed to read from DHT sensor! Check your wires."));
    return;
  }

  // --- CALIBRATION SECTION ---
  // The offset we calculated based on your weather app
  float tempOffset = -2.5; 
  
  // Apply the offset to get the true temperature
  float calibratedTemp = rawTemp + tempOffset;

  // Print the results to your screen
  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  |  Temperature: "));
  Serial.print(calibratedTemp); // Prints the corrected temperature
  Serial.println(F("°C "));
}