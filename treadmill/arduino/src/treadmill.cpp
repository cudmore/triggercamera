/*
 * Author: Robert Cudmore
 * http://robertcudmore.org
 * 20160214
 *
 * Purpose: Run a trial based experiment
 *   
 *    
 *
 */

//For information on exposing low-vevel interrupts on Arduino Uno
// http://www.geertlangereis.nl/Electronics/Pin_Change_Interrupts/PinChange_en.html

#include "Arduino.h"
//#include "main.h"

#include <AccelStepper.h> // http://www.airspayce.com/mikem/arduino/AccelStepper/index.html
#include <Encoder.h> // http://www.pjrc.com/teensy/td_libs_Encoder.html

//Uncomment this line if running on an Arduino Uno and compiling with the arduino IDE
//#define _expose_interrupts_ 1

//trial - epoch - pulse

struct trial
{
	boolean trialIsRunning;
	int trialNumber;
	unsigned long trialStartMillis;
	unsigned long trialDur; //ms, numEpoch*epochDur
	//
	int currentEpoch;
	unsigned int epochDur;
	unsigned int numEpoch;
	unsigned long epochStartMillis;
	//
	unsigned int currentPulse; //count 0,1,2,... as we run
	unsigned long pulseStartMillis; //millis at start of currentPulse
	//user specified parameters
	unsigned long  preDur; //ms
	unsigned long  postDur; //ms
	int numPulse;
	int pulseDur; //ms
	int useMotor;
	unsigned long motorDel; //ms
	unsigned long motorDur; //ms
	unsigned long motorSpeed; //ms

};

unsigned long msIntoTrial;
unsigned long msIntoEpoch;
unsigned long tmpPulseDur;
boolean inPre;
boolean inPulse;
boolean inPost;
int tmpEpoch;

struct steppermotor
{
   boolean useMotor;
   boolean isRunning;
   int maxSpeed;
   int stepPin;
   int dirPin;
   int resetPin;
};

struct rotaryencoder
{
	int pinA; // use pin 2
	int pinB; // use pin 3
};

struct simulatescanimage
{
	int isOn;
	int frameInterval; //millis
	int numFrames;
	int currentFrame;
	unsigned long lastFrameMillis;
};

//char versionStr[] = "main.cpp 20160306";
String versionStr = "20160322";
typedef struct trial Trial;
typedef struct steppermotor StepperMotor;
typedef struct rotaryencoder RotaryEncoder;
typedef struct simulatescanimage SimulateScanImage;

Trial trial;
StepperMotor motor;
RotaryEncoder rotaryencoder;
SimulateScanImage si;

//stepper and myEncoder are the variable names we will use below
AccelStepper stepper(AccelStepper::DRIVER,motor.stepPin,motor.dirPin);
Encoder myEncoder(rotaryencoder.pinA, rotaryencoder.pinB);

// used in xxx callbacks
volatile int goReceived = 0;    //A0
volatile int stopReceived = 0;  //A1
volatile int siIsUp = 0;      //A2
volatile int gotFrame = 0;      //A2

/////////////////////////////////////////////////////////////
//callback for frame clock pin using xxx
void InitializeIO() {
  pinMode(A0, INPUT);
  digitalWrite(A0, LOW);
  pinMode(A1, INPUT);
  digitalWrite(A1, LOW);
  pinMode(A2, INPUT);
  digitalWrite(A2, LOW);
}
/////////////////////////////////////////////////////////////
//turn off this definition for teensy
#if defined(_expose_interrupts_)
void InitializeInterrupt() {
  cli();
  PCICR =0x02;
  PCMSK1 = 0b00000111;
  sei();
}
/////////////////////////////////////////////////////////////
ISR(PCINT1_vect) {
  if (digitalRead(A0)==1) goReceived=1; 
  if (digitalRead(A1)==1) stopReceived=1; 
  if (digitalRead(A2)==1) siIsUp=1; else gotFrame=1;
}
#endif

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////
void setup()
{
  //
  //trial
  trial.trialIsRunning = false;
  trial.trialNumber = 0;
  trial.trialStartMillis = 0;
  trial.epochDur = 1000; // epoch has to be >= (preDur + xxx + postDur)
  trial.numEpoch = 1;
  
  trial.trialDur = (trial.numEpoch*trial.epochDur); //* (numPulse*pulseDur);

  trial.useMotor = 1;
  trial.motorDel = 200; //within each pulse
  trial.motorDur = 200;

  trial.preDur = 1000;
  trial.postDur = 1000;

  trial.numPulse = 3;
  trial.pulseDur = 1000;
  //
  //motor
  motor.useMotor = true;
  motor.isRunning = false;
  //motor.speed = xxx;
  //motor.maxSpeed = xxx;
  //motor.stepPin = xxx;
  //motor.dirPin = xxx;
  //motor.resetPin = xxx;
  //
  //rotary encoder
  //encoder.pinA = xxx;
  //encoder.pinB = xxx;
  //
  //simulate scan image
  si.isOn = 1;
  si.frameInterval = 400; //millis
  si.numFrames = 10;
  si.currentFrame = 0;
  si.lastFrameMillis = 0;
  
  //pinMode(LED_BUILTIN, OUTPUT);
  pinMode(13, OUTPUT);
  
  //Serial.begin(115200);
  Serial.begin(115200);

  #if defined(_expose_interrupts_)
	InitializeIO();
	InitializeInterrupt();
  #endif
  
}

/////////////////////////////////////////////////////////////
void serialOut(unsigned long now, String str, unsigned long val) {
	Serial.println(String(now) + "," + str + "," + val);
}
/////////////////////////////////////////////////////////////
void scanImageStart_(unsigned long now) {
	if (si.isOn) {
		si.currentFrame = 0;
		si.lastFrameMillis = millis();
		serialOut(now, "scanimagestart", si.currentFrame);
	}
}
/////////////////////////////////////////////////////////////
void scanImageFrame_(unsigned long now) {
	if (trial.trialIsRunning && si.isOn) {
		if (now > (si.lastFrameMillis + si.frameInterval)) {
			serialOut(now, "scanimageframe", si.currentFrame);
			si.lastFrameMillis = millis();
			si.currentFrame += 1;
		}
	}
}
/////////////////////////////////////////////////////////////
void scanImageStop_() {

}
/////////////////////////////////////////////////////////////
void startTrial(unsigned long now) {
	if (trial.trialIsRunning==0) {
		trial.trialNumber += 1;
		
		trial.trialStartMillis = now;
		trial.epochStartMillis = now;

		//trial.trialDur = trial.preDur + (trial.numPulse * trial.pulseDur) + trial.postDur;
		trial.trialDur = trial.epochDur * trial.numEpoch;
		trial.currentEpoch = 0;
		trial.currentPulse = 0;
		
		serialOut(now, "startTrial", trial.trialNumber);

		trial.trialIsRunning = 1;
		
		scanImageStart_(now);
	}
}
/////////////////////////////////////////////////////////////
void stopTrial(unsigned long now) {
	if (trial.trialIsRunning==1) {
		trial.trialIsRunning = 0;
		motor.isRunning = false; //make sure motor is NOT running
		serialOut(now, "stopTrial", trial.trialNumber);
	}
}
/////////////////////////////////////////////////////////////
void GetState() {
	//trial
	Serial.println("trialNumber=" + String(trial.trialNumber));
	Serial.println("trialDur=" + String(trial.trialDur));

	Serial.println("numEpoch=" + String(trial.numEpoch));
	Serial.println("epochDur=" + String(trial.epochDur));

	Serial.println("preDur=" + String(trial.preDur));
	Serial.println("postDur=" + String(trial.postDur));

	Serial.println("numPulse=" + String(trial.numPulse));
	Serial.println("pulseDur=" + String(trial.pulseDur));

	Serial.println("useMotor=" + String(trial.useMotor));
	Serial.println("motorDel=" + String(trial.motorDel));
	Serial.println("motorDur=" + String(trial.motorDur));
	//motor
	Serial.println("motorSpeed=" + String(trial.motorSpeed));
	Serial.println("motorMaxSpeed=" + String(motor.maxSpeed));

	Serial.println("versionStr=" + String(versionStr));
	//scanimage
	//Serial.println("si.isOn=" + String(si.isOn));
	//Serial.println("si.frameInterval=" + String(si.frameInterval));
	//Serial.println("si.numFrames=" + String(si.numFrames));
}
/////////////////////////////////////////////////////////////
void SetTrial(String name, String strValue) {
	int value = strValue.toInt();
	//trial
	if (name == "numPulse") {
		trial.numPulse = value;
		Serial.println("trial.numPulse=" + String(trial.numPulse));

	} else if (name=="numEpoch") {
		trial.numEpoch = value;
		Serial.println("trial.numEpoch=" + String(trial.numEpoch));
	} else if (name=="epochDur") {
		trial.epochDur = value;
		Serial.println("trial.epochDur=" + String(trial.epochDur));

	} else if (name=="preDur") {
		trial.preDur = value;
		Serial.println("trial.preDur=" + String(trial.preDur));
	} else if (name=="postDur") {
		trial.postDur = value;
		Serial.println("trial.postDur=" + String(trial.postDur));

	} else if (name=="pulseDur") {
		trial.pulseDur = value;
		Serial.println("trial.pulseDur=" + String(trial.pulseDur));
	} else if (name=="useMotor") {
		if (strValue=="motorOn") {
			trial.useMotor = true;
		} else {
			trial.useMotor = false;
		}
		Serial.println("trial.useMotor=" + String(trial.useMotor));
	} else if (name=="motorDel") {
		trial.motorDel = value;
		Serial.println("trial.motorDel=" + String(trial.motorDel));
	} else if (name=="motorDur") {
		trial.motorDur = value;
		Serial.println("trial.motorDur=" + String(trial.motorDur));
	} else if (name=="motorSpeed") {
		trial.motorSpeed = value;
		Serial.println("trial.motorSpeed=" + String(trial.motorSpeed));
	//scanimage
	//} else if (name == "si.isOn") {
	//	si.isOn = value;
	//} else if (name == "si.frameInterval") {
	//	si.frameInterval = value;
	//} else if (name == "si.numFrames") {
	//	si.numFrames = value;
	//error
	} else {
		Serial.println("SetValue() did not handle '" + name + "'");
	}
	
}
/////////////////////////////////////////////////////////////
//respond to incoming serial
void SerialIn(unsigned long now, String str) {
	String delimStr = ",";
		
	if (str.length()==0) {
		return;
	}
	if (str == "version") {
		Serial.println("version=" + versionStr);
	} else if (str == "startTrial") {
		startTrial(now);
	}
	else if (str == "stopTrial") {
		stopTrial(now);
	}
	else if (str.startsWith("getState")) {
		GetState();
	}
	else if (str.startsWith("settrial")) {
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

/////////////////////////////////////////////////////////////
void updateMotor(unsigned long now) {
	//maybe add a global 'useMotor' state variable
	if (trial.trialIsRunning && trial.useMotor && inPulse) {
		unsigned long motorStart = trial.pulseStartMillis + trial.motorDel;
		unsigned long motorStop = motorStart + trial.motorDur;
		if (!motor.isRunning && (now >= motorStart) && (now < motorStop)) {
			digitalWrite(13, HIGH);
			motor.isRunning = true;
			serialOut(now, "motorstart", trial.currentPulse);
		} else if (motor.isRunning && (now > motorStop)) {
			digitalWrite(13, LOW);
			motor.isRunning = false;
			serialOut(now, "motorstop", trial.currentPulse);
		}
		if (motor.isRunning) {
			stepper.runSpeed();
		}
	}
}
/////////////////////////////////////////////////////////////
void loop()
{
  //digitalWrite(LED_BUILTIN, HIGH); //so we can see if the code is running
  //digitalWrite(13, HIGH); //so we can see if the code is running

	unsigned long now = millis();
	msIntoTrial = now-trial.trialStartMillis;
	msIntoEpoch = now-trial.epochStartMillis;
	
	//update epoch
	if (trial.trialIsRunning) {
		tmpEpoch = floor(msIntoTrial / trial.epochDur);
		if ((tmpEpoch != trial.currentEpoch) && (tmpEpoch < trial.numEpoch)) {
			trial.epochStartMillis = now;
			msIntoEpoch = now-trial.epochStartMillis;
			trial.currentEpoch = tmpEpoch;
			serialOut(now, "startEpoch", trial.currentEpoch);		
		}
	}
	
	tmpPulseDur = trial.numPulse * trial.pulseDur;
	inPre = msIntoEpoch < trial.preDur;
	inPulse = (msIntoEpoch > trial.preDur) && (msIntoEpoch < (trial.preDur + tmpPulseDur));
	inPost = msIntoEpoch > (trial.preDur + tmpPulseDur);
	
	if (Serial.available() > 0) {
		String inString = Serial.readStringUntil('\n');
		inString.replace("\n","");
		inString.replace("\r","");
		SerialIn(now, inString);
	}

	if (now > (trial.trialStartMillis + trial.trialDur)) {
		stopTrial(now);
	}

    //updatePulse (will only be value during inPulse)
    if (inPulse) {
    	trial.currentPulse = floor((msIntoEpoch-trial.preDur) / trial.pulseDur);
		trial.pulseStartMillis = trial.epochStartMillis + trial.preDur + (trial.currentPulse * trial.pulseDur);
	}
	
  	updateMotor(now);
  	
	scanImageFrame_(now);

	//simulat rotary encoder while motor is running
	if (motor.isRunning) {
		long rnd = random(0,100);
		if (rnd>90) {
			//serialOut(now, "rotary", 1);
		}
	}
	
	delay(2); //ms

}
