//20160528
//Robert H Cudmore
//
// A class to simulate a trigger and frame pins of a microscope
//
// Two version
//	 - scanimage, one pin that goes high on trigger and then pulses low for frame
//	 - two pins, two different pins, one for trigger and another for frame
//
// When this code is running on an Arduino, connect triggerPin and framePin to devices to be triggered
// The beauty is these ppins can be looped back to the same Arduino as inputs
//
// Usage:
//	
//	int triggerPin = 2;
//	int framePin = 3;
//	int ledPin = 13;
//	bSimulateScope myScope(triggerPin, framePin, ledPin);
//
//	myScope.set("frameInterval", 30);
//	myScope.set("numFrames", 150);
//
//	void loop()
//	{
//		myScope.Update();
//	}

#include "Arduino.h"

class bSimulateScope
{
	// Class Member Variables
	int triggerPin;
	int framePin;
	int ledPin;      // the number of the LED pin
	
	// These maintain the current state
	int ledState;             		// ledState used to set the LED
	unsigned long previousMillis;  	// will store last time LED was updated

	//copied from v2.cpp
	String inString; //to receive serial input
	boolean useTwoTriggerPins;
 	boolean isRunning;
 	int currentFrame;
 	unsigned long trialStartMillis;
 	unsigned long lastFrameMillis;
 	int frameInterval; //ms
 	int framePinDur; //ms, duration of pulse for frame pin, 0 for none
 	int numFrames;
 	
  // Constructor - creates a bSimulateScope 
  // and initializes the member variables and state
  public:
  bSimulateScope(int theTriggerPin, int theFramePin, int theLedPin)
  {
	triggerPin = theTriggerPin; //goes high during scanning
	framePin = theFramePin;

	pinMode(triggerPin, OUTPUT);     
	pinMode(framePin, OUTPUT);     

	ledPin = theLedPin;
	pinMode(ledPin, OUTPUT);     
	  
	previousMillis = 0;
	
	Serial.begin(115200);

	//copied from v2.cpp
	inString = "";
	useTwoTriggerPins = false;
	isRunning = false;
	currentFrame = 0;
	trialStartMillis = 0; // not sure on 0 ???
	lastFrameMillis = 0;
	frameInterval = 30; //ms
	framePinDur = 5;
	numFrames = 150;
  }
 
	/////////////////////////////////////////////////////////////////
	void help() {
		Serial.println("serial commands are:");	
		Serial.println("start : start a trial");	
		Serial.println("help : print this help");	
		Serial.println("state : print state variables");	
	}
	/////////////////////////////////////////////////////////////////
	void state() {
		Serial.println("triggerPin=" + String(triggerPin));	
		Serial.println("framePin=" + String(framePin));	
		Serial.println("ledPin=" + String(ledPin));	
		Serial.println("useTwoTriggerPins=" + String(useTwoTriggerPins));	
		Serial.println("frameInterval=" + String(frameInterval));	
		Serial.println("numFrames=" + String(numFrames));	
		Serial.println("framePinDur=" + String(framePinDur));	
	}
	/////////////////////////////////////////////////////////////
	void serialOut(unsigned long now, String str, unsigned long val) {
		Serial.println(String(now) + "," + str + "," + val);
	}
	/////////////////////////////////////////////////////////////////
	void SerialIn(unsigned long now, String str) {
		str.replace("\n","");
		str.replace("\r","");

		String delimStr = ",";
		
		if (str.length()==0) {
			return;
		}	
		else if (str == "help") {
			help();
		}
		else if (str == "state") {
			state();
		}
		else if (str == "start") {
			trialStart(now);
		}
	}
	/////////////////////////////////////////////////////////////
	void trialStart(unsigned long now) {
		if (isRunning == false) {
			if (useTwoTriggerPins) {
				digitalWrite(triggerPin, HIGH); //
			} else {
				digitalWrite(framePin, HIGH); //
			}
		
			isRunning = true;
			currentFrame = 0;
			trialStartMillis = now;
			serialOut(now, "trialStart", currentFrame);
		}
	}
	/////////////////////////////////////////////////////////////
	void trialStop(unsigned long now) {
		if (isRunning) {
			if (useTwoTriggerPins) {
				digitalWrite(triggerPin, LOW); //
			} else {
				digitalWrite(framePin, LOW); //
			}
			isRunning = false;
			serialOut(now, "trialStop", currentFrame);
		}
	}
	/////////////////////////////////////////////////////////////
	void set(String param, int value) {
		if (param == "frameInterval") {
			frameInterval = value;
		} else if (param == "numFrames") {
			numFrames = value;
		} else if (param == "framePinDur") {
			framePinDur = value;
		} else {
			Serial.println("bSimulateScope::set() did not understand '" + param + "'");
		}
	}
		
  /////////////////////////////////////////////////////////////////
  void Update()
  {
    unsigned long now = millis();
     
	if (Serial.available() > 0) {
		inString = Serial.readStringUntil('\n');
		SerialIn(now, inString);
	}

	//update scope frames
	if (isRunning) {
		if (now > (lastFrameMillis + frameInterval)) {
			lastFrameMillis = now;
			currentFrame += 1;
  			digitalWrite(ledPin, LOW); //so we can see if the code is running

  			if (useTwoTriggerPins) {
  				digitalWrite(framePin, HIGH); //so we can see if the code is running
  				if (framePinDur > 0) delay(framePinDur);
  				digitalWrite(framePin, LOW); //so we can see if the code is running
  			} else {
  				digitalWrite(framePin, LOW); //so we can see if the code is running
   				if (framePinDur > 0) delay(framePinDur);
 				digitalWrite(framePin, HIGH); //so we can see if the code is running
			}
			
			serialOut(now, "newFrame", currentFrame);

			if (currentFrame == numFrames) {
				trialStop(now);
			}
		} else {
			digitalWrite(ledPin, HIGH); //so we can see if the code is running
		}
	} else {
		digitalWrite(ledPin, LOW); //so we can see if the code is running
	} //isRunning

  } //update
  
}; // class

// start of main Arduino code
int triggerPin = 2;
int framePin = 3;
int ledPin = 13;

bSimulateScope myScope(triggerPin, framePin, ledPin);
 
void setup()
{
}
 
void loop()
{
	myScope.Update();
}
