/**
 * Blink
 *
 * Turns on an LED on for one second,
 * then off for one second, repeatedly.
 */
#include "Arduino.h"

int outPin = 4;
int numTrials = 1;
int currTrial = 0;

long frameInterval = 50; //ms
int numFrames = 20;
int currFrame = 0;
unsigned long lastFrame = 0; //ms

unsigned long now;

void setup()
{
  // initialize LED digital pin as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(outPin, OUTPUT);
}

void loop()
{
  now = millis();
  
  // turn the LED on (HIGH is the voltage level)
  //digitalWrite(LED_BUILTIN, HIGH);

  if (currTrial < numTrials) {
	digitalWrite(LED_BUILTIN, HIGH);

  	digitalWrite(outPin, HIGH);
  	delay(5000);
  	digitalWrite(outPin, LOW);
	currTrial += 1;

	digitalWrite(LED_BUILTIN, LOW);
  } else {
  
  }
  
  delay(1000);
}