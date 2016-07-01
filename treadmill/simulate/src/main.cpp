/*
 Author: Robert Cudmore
 http://robertcudmore.org
 20160422

 Purpose: Simulate a piece of hardware
   
 This implementation simulates ScanImage:
   (1) wait for a trigger on triggerPin
   (2) once trigger is received, send numFrames at interval frameInterval on framePin
   (3) use serial interface to set up parameters {numFrames, frameInterval}
   (4) start and stop a trial with serial {startTrial, stopTrial}
   (5) get state with serial getState
 
 serial commands are
 ===================
 setTrial,numFrames,20
 setTrial,frameInterval,500
 trialStart
 trialStop
 getState
 
*/

#include "Arduino.h"

struct trial {
	boolean isRunning;
	int currentFrame;
	unsigned long trialStartMillis;
	unsigned long lastFrameMillis;

	int numFrames;
	int frameInterval; //ms
	
	int triggerPin;
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

  trial.numFrames = 10;
  trial.frameInterval = 200; //ms

  trial.triggerPin = 0;
  trial.framePin = 1;
  trial.ledPin = 13;
  
  Serial.begin(115200);

  pinMode(trial.triggerPin, INPUT);
  pinMode(trial.framePin, OUTPUT);
  pinMode(trial.framePin, OUTPUT);
  
  Serial.println("simulate.cpp is ready");
  
}

/////////////////////////////////////////////////////////////
void serialOut(unsigned long now, String str, unsigned long val) {
	Serial.println(String(now) + "," + str + "," + val);
}

/////////////////////////////////////////////////////////////
void scanImageStart(unsigned long now) {
	if (trial.isRunning == false) {
		trial.isRunning = true;
		trial.currentFrame = 0;
		trial.trialStartMillis = millis();
		serialOut(now, "scanimagestart", trial.currentFrame);
	}
}
/////////////////////////////////////////////////////////////
void scanImageStop(unsigned long now) {
	if (trial.isRunning) {
		serialOut(now, "scanImageStop", trial.currentFrame);
		trial.isRunning = false;
	}
}
/////////////////////////////////////////////////////////////
//if running, increment to next frame and stop if necessary
void scanImageFrame(unsigned long now) {
	if (trial.isRunning) {
		if (now > (trial.lastFrameMillis + trial.frameInterval)) {
			trial.lastFrameMillis = now;
			trial.currentFrame += 1;
			serialOut(now, "scanImageFrame", trial.currentFrame);
  			digitalWrite(trial.ledPin, LOW); //so we can see if the code is running
			if (trial.currentFrame==trial.numFrames) {
				scanImageStop(now);
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
	else if (str == "startTrial") {
		scanImageStart(now);
	}
	else if (str == "stopTrial") {
		scanImageStop(now);
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
  //digitalWrite(LED_BUILTIN, HIGH); //so we can see if the code is running
  //digitalWrite(13, HIGH); //so we can see if the code is running

	now = millis();
	msIntoTrial = now - trial.trialStartMillis;
	msIntoFrame = now - trial.lastFrameMillis;

	if (Serial.available() > 0) {
		inString = Serial.readStringUntil('\n');
		inString.replace("\n","");
		inString.replace("\r","");
		SerialIn(now, inString);
	}


  	scanImageFrame(now);
  	
  	//digitalWrite(trial.ledPin, LOW); //so we can see if the code is running
	//delay(250);
  	//digitalWrite(trial.ledPin, HIGH); //so we can see if the code is running
	//delay(250);

}
