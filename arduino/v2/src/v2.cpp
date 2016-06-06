/*
 Author: Robert Cudmore
 http://robertcudmore.org
 20160422

 Purpose: Simulate a piece of hardware
   
 This implementation simulates ScanImage:
   (1) wait for a trigger on triggerPin
   (2) once trigger is received, set trialPin high and send numFrames at interval frameInterval on framePin
   (3) use serial interface to set up parameters {numFrames, frameInterval}
   (4) start and stop a trial with serial {startTrial, stopTrial}
   (5) get state with serial getState
 
 serial commands are
 ===================
 setTrial,numFrames,20
 setTrial,frameInterval,500
 startTrial
 stopTrial
 getState
 
 changle log:
 20160521, added trial.useTwoTriggerPins to switch between Bruger style trigger (two pins) and scanimage trigger (one pin)
     No serial interface for this, hand-modify code and re-upload to Arduino to switch between these two
     
     Added trial.framePinDur to control duration of pulse during frame
     
*/

#include "Arduino.h"

struct trial {
	boolean isRunning;
	int currentFrame;
	unsigned long trialStartMillis;
	unsigned long lastFrameMillis;

	int numFrames;
	int frameInterval; //ms
	
	int useTwoTriggerPins;
	
	int framePinDur;
	
	int triggerPin;
	int trialPin;
	int framePin;
	int ledPin;
};

typedef struct trial Trial;
Trial trial;

/////////////////////////////////////////////////////////////
void setup()
{
  trial.isRunning = false;
  trial.currentFrame = 0;
  trial.trialStartMillis = 0;
  trial.lastFrameMillis = 0;

  trial.numFrames = 600;
  trial.frameInterval = 30; //ms

  trial.useTwoTriggerPins = true;
  trial.framePinDur = 5; //in milliseconds, set to 0 for no duration
  trial.triggerPin = 0; //to externally trigger the Arduino
  trial.trialPin = 6; //set high during a trial
  trial.framePin = 4; //unified scan image pin, high during scan, low pulses for each frame
  trial.ledPin = 13;
  
  Serial.begin(115200);

  pinMode(trial.triggerPin, INPUT);
  pinMode(trial.trialPin, OUTPUT);
  pinMode(trial.framePin, OUTPUT);
  
  digitalWrite(trial.trialPin, LOW);
  digitalWrite(trial.framePin, LOW);
  
  Serial.println("v2.cpp is ready");
  
}

/////////////////////////////////////////////////////////////
void help(unsigned long now) {
	Serial.println("serial commands are");
	Serial.println("setTrial,numFrames,20");
	Serial.println("setTrial,frameInterval,500");
	Serial.println("startTrial");
	Serial.println("stopTrial");
	Serial.println("getState");
}

/////////////////////////////////////////////////////////////
void serialOut(unsigned long now, String str, unsigned long val) {
	Serial.println(String(now) + "," + str + "," + val);
}

/////////////////////////////////////////////////////////////
void trialStart(unsigned long now) {
	if (trial.isRunning == false) {
  		if (trial.useTwoTriggerPins) {
  			digitalWrite(trial.trialPin, HIGH); //
  		} else {
  			digitalWrite(trial.framePin, HIGH); //
		}
		
		trial.isRunning = true;
		trial.currentFrame = 0;
		trial.trialStartMillis = millis();
		serialOut(now, "trialStart", trial.currentFrame);
	}
}
/////////////////////////////////////////////////////////////
void trialStop(unsigned long now) {
	if (trial.isRunning) {
  		if (trial.useTwoTriggerPins) {
  			digitalWrite(trial.trialPin, LOW); //
  		} else {
  			digitalWrite(trial.framePin, LOW); //
		}
		serialOut(now, "trialStop", trial.currentFrame);
		trial.isRunning = false;
	}
}
/////////////////////////////////////////////////////////////
//if running, increment to next frame and stop if necessary
void newFrame(unsigned long now) {
	if (trial.isRunning) {
		if (now > (trial.lastFrameMillis + trial.frameInterval)) {
			trial.lastFrameMillis = now;
			trial.currentFrame += 1;
  			digitalWrite(trial.ledPin, LOW); //so we can see if the code is running

  			if (trial.useTwoTriggerPins) {
  				digitalWrite(trial.framePin, HIGH); //so we can see if the code is running
  				if (trial.framePinDur > 0) delay(trial.framePinDur);
  				digitalWrite(trial.framePin, LOW); //so we can see if the code is running
  			} else {
  				digitalWrite(trial.framePin, LOW); //so we can see if the code is running
   				if (trial.framePinDur > 0) delay(trial.framePinDur);
 				digitalWrite(trial.framePin, HIGH); //so we can see if the code is running
			}
			
			serialOut(now, "newFrame", trial.currentFrame);

			if (trial.currentFrame==trial.numFrames) {
				trialStop(now);
			}
		} else {
			digitalWrite(trial.ledPin, HIGH); //so we can see if the code is running
		}
	} else {
		digitalWrite(trial.ledPin, LOW); //so we can see if the code is running
	} //isRuunning
}
/////////////////////////////////////////////////////////////
void SetTrial(String name, String strValue) {
	int value = strValue.toInt();
	//trial
	if (name == "numFrames") {
		trial.numFrames = value;
		Serial.println("trial.numFrames=" + String(trial.numFrames));
	} else if (name=="frameInterval") {
		trial.frameInterval = value;
		Serial.println("trial.frameInterval=" + String(trial.frameInterval));

	//error
	} else {
		Serial.println("SetValue() did not handle '" + name + "'");
	}	
}
/////////////////////////////////////////////////////////////
void GetState() {
	Serial.println("isRunning=" + String(trial.isRunning));
	Serial.println("currentFrame=" + String(trial.currentFrame));

	Serial.println("numFrames=" + String(trial.numFrames));
	Serial.println("frameInterval=" + String(trial.frameInterval));

	Serial.println("triggerPin=" + String(trial.triggerPin));
	Serial.println("framePin=" + String(trial.framePin));
	Serial.println("ledPin=" + String(trial.ledPin));	
}
/////////////////////////////////////////////////////////////
//respond to incoming serial
void SerialIn(unsigned long now, String str) {
	String delimStr = ",";
		
	if (str.length()==0) {
		return;
	}	
	else if (str == "help") {
		help(now);
	}
	else if (str == "startTrial") {
		trialStart(now);
	}
	else if (str == "stopTrial") {
		trialStop(now);
	}
	else if (str.startsWith("getState")) {
		GetState();
	}
	else if (str.startsWith("setTrial")) {
		//set is {set,name,value}
		int firstComma = str.indexOf(delimStr,0);
		int secondComma = str.indexOf(delimStr,firstComma+1);
		String nameStr = str.substring(firstComma+1,secondComma); //first is inclusive, second is exclusive
		String valueStr = str.substring(secondComma+1,str.length());
		SetTrial(nameStr, valueStr);
	}
	else {
		Serial.println("SerialIn() did not handle: '" + str + "'");
	}
		
}

//global
unsigned long now;
unsigned long msIntoTrial;
unsigned long msIntoFrame;
String inString; //to receive serial input

/////////////////////////////////////////////////////////////
void loop()
{

	now = millis();
	msIntoTrial = now - trial.trialStartMillis;
	msIntoFrame = now - trial.lastFrameMillis;

	// add code to listen to trial.triggerPin
	
	if (Serial.available() > 0) {
		inString = Serial.readStringUntil('\n');
		inString.replace("\n","");
		inString.replace("\r","");
		SerialIn(now, inString);
	}

  	newFrame(now);
  	
}