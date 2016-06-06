#include "Arduino.h"
#include "bSimulateScope.h"

//experiment will manage 2 triggers (trial and frame) that need to talk to each other
//experiment will also be passthrough for both (trial and frame)

//todo: hard-wire a switch to a GPIO to set isArmed_

//define these in easily editable header
/*
kMaxFrames

//frame interrupts???

outTrialPin
outFramePin

*/

const int kMaxFrames = 12000; //9000;

class bExperiment {
  static void isr0();
  static void isr1();
  
  static bExperiment * instance0_;
  static bExperiment * instance1_;
      
  public:
    bExperiment();
	void handleTrialInterrupt(); //virtual so derived classes can over-ride
	void handleFrameInterrupt(); //virtual so derived classes can over-ride

    void begin();
	void serialPrint();
	boolean SerialIn(unsigned long now, String str);
	
  private:
  	boolean isArmed_;
  	volatile int isRunning_;
  	volatile unsigned long lastStartTime_;
  	volatile unsigned long lastStopTime_;

  	volatile int frameNumber_;
  	volatile int lastFrameTime_;
      
    unsigned long frames[kMaxFrames];
    
    int outTrialPin;
    int outFramePin;
    
    int outFramePinDelay; //ms
    
};  // end of class bExperiment

/////////////////////////////////////////////////////////////////////
// constructor
bExperiment::bExperiment() {
    isArmed_ = false;
    isRunning_ = 0;
    lastStartTime_ = 0;
    lastStopTime_ = 0;

    frameNumber_ = 0;
    lastFrameTime_ = 0;
    
    outTrialPin = 10;
    outFramePin = 11;
}
/////////////////////////////////////////////////////////////////////
//whichType: RISING, FALLING, CHANGE
void bExperiment::begin() {
	
	int trialTrigger = 22;
	int frameTrigger = 23;
	
	pinMode(trialTrigger, INPUT);
	attachInterrupt (trialTrigger, isr0, CHANGE); 
	instance0_ = this;

	pinMode(frameTrigger, INPUT);
	attachInterrupt (frameTrigger, isr1, RISING); 
	instance1_ = this;
		
	pinMode(outTrialPin, OUTPUT);
	pinMode(outFramePin, OUTPUT);
}
/////////////////////////////////////////////////////////////////////
// ISR glue routines
void bExperiment::isr0() {
  instance0_->handleTrialInterrupt();  
}
/////////////////////////////////////////////////////////////////////
void bExperiment::isr1() {
  instance1_->handleFrameInterrupt();  
}
/////////////////////////////////////////////////////////////////////  
// for use by ISR glue routines
bExperiment * bExperiment::instance0_;
bExperiment * bExperiment::instance1_;
/////////////////////////////////////////////////////////////////////  
void bExperiment::handleTrialInterrupt() {
  isRunning_ = ! isRunning_;
  if (isRunning_) {
	lastStartTime_ = millis();
	frameNumber_ = 0;
	digitalWrite(outTrialPin, HIGH);
	//Serial.println("                bExperiment::handleTrialInterrupt() HIGH");
  } else {
	lastStopTime_ = millis();
	digitalWrite(outTrialPin, LOW);
	//Serial.println("                bExperiment::handleTrialInterrupt() LOW");
	//serialPrint();
  }
}
/////////////////////////////////////////////////////////////////////  
void bExperiment::handleFrameInterrupt() {
	if (isRunning_) {
		//don't ever go past kMaxFrames
		if (frameNumber_ < kMaxFrames) {
			lastFrameTime_ = millis();
			frames[frameNumber_] = lastFrameTime_;
			frameNumber_++;
			digitalWrite(outFramePin, HIGH);
			//do not EVER call delay() from an ISR interrupt !!!!
			//if (outFramePinDelay>0) { delay(outFramePinDelay); }
			digitalWrite(outFramePin, LOW);
			//Serial.println("                bExperiment::handleFrameInterrupt() " + String(frameNumber_));
		}
	}
}
/////////////////////////////////////////////////////////////////////  
void bExperiment::serialPrint() {
	int i;
	//Serial.println("=== bExperiment::serialPrint() ===");
	//Serial.println("millis,absmillis,event,frame");
	Serial.println("absmillis,event,frame");
	Serial.println(String(lastStartTime_-lastStartTime_) + ",ardTrialStart,");
	//Serial.println(String(lastStartTime_) + "," + String(lastStartTime_-lastStartTime_) + ",trialStart,");
	for (i=0; i<frameNumber_; i++) {
		delay(10); //ms, this is required otherwise reading serial in python runs out of buffer space
		//Serial.println(String(frames[i]) + "," + String(frames[i] - lastStartTime_) + ",frame," + String(i));
		Serial.println(String(frames[i] - lastStartTime_) + ",ardFrame," + String(i));
	}
	delay(10);
	//Serial.println(String(lastStopTime_) + "," + String(lastStopTime_-lastStartTime_) + ",ardTrialStop," + String(frameNumber_));
	Serial.println(String(lastStopTime_-lastStartTime_) + ",ardTrialStop," + String(frameNumber_));
}
/////////////////////////////////////////////////////////////////
boolean bExperiment::SerialIn(unsigned long now, String str) {
	str.replace("\n","");
	str.replace("\r","");

	String delimStr = ",";
	
	if (str.length()==0) {
		return false;
	}	
	else if (str == "help") {
		//help();
	}
	else if (str == "trial") { //get frame times of last trial
		serialPrint();
	}
	else if (str == "start") {
		//trialStart(now);
	} else {
		return false;
	}
	return true;
}

/////////////////////////////////////////////////////////////////////  
// User Code
/////////////////////////////////////////////////////////////////////  

bExperiment myExperiment;

int triggerPin = 20; //trial
int framePin = 21; //frame
int ledPin = 13;
bSimulateScope fakeScope(triggerPin, framePin, ledPin);

void setup() {
	//Serial.begin(115200);
	Serial.begin(9600);

	myExperiment.begin();

	//fakeScope.set("numFrames", 300);
	//fakeScope.set("numFrames", 1800);
	fakeScope.set("numFrames", 1800);
}

unsigned long now;
String inString;
boolean serialHandled;

void loop() {
	now = millis();
	
	if (Serial.available() > 0) {
		inString = Serial.readStringUntil('\n');
		serialHandled = fakeScope.SerialIn(now, inString);
		serialHandled = myExperiment.SerialIn(now, inString);
	}
	
	fakeScope.Update();	
}

