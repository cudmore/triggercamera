//http://forum.arduino.cc/index.php?topic=160101.0

//Arduino Uno only has 2 interrupts {0, 1}

#include "Arduino.h"
#include "bSimulateScope.h"

class bTrigger {
  static void isr0();
  static void isr1();
  
  const byte whichISR_; //Uno only has 2 interrupts (0,1), THESE DO NOT REFER TO PINS
  
  static bTrigger * instance0_;
  static bTrigger * instance1_;
    
  volatile int counter_;
  volatile unsigned long lastTriggerTime;
  
  public:
    bTrigger(const byte which0);
	virtual void handleInterrupt(); //virtual so derived classes can over-ride
    void begin(int whichType);
    void resetCount() { counter_ = 0; }
    int getCount() { return counter_; }
    unsigned long getLastTime() { return lastTriggerTime; }
    
};  // end of class bTrigger

/////////////////////////////////////////////////////////////////////
//whichType: RISING, FALLING, CHANGE
void bTrigger::begin(int whichType) {
	switch (whichISR_) {
		case 0: 
		  attachInterrupt (0, isr0, whichType); 
		  instance0_ = this;
		  break;
		case 1: 
		  attachInterrupt (1, isr1, whichType); 
		  instance1_ = this;
		break;
	}  
		
}  // end of bTrigger::begin 
/////////////////////////////////////////////////////////////////////
// constructor
bTrigger::bTrigger(const byte whichISR) : whichISR_(whichISR) {
    counter_ = 0;
}
/////////////////////////////////////////////////////////////////////
// ISR glue routines
void bTrigger::isr0() {
  instance0_->handleInterrupt();  
}
/////////////////////////////////////////////////////////////////////
void bTrigger::isr1() {
  instance1_->handleInterrupt();  
}
/////////////////////////////////////////////////////////////////////  
// for use by ISR glue routines
bTrigger * bTrigger::instance0_;
bTrigger * bTrigger::instance1_;
/////////////////////////////////////////////////////////////////////  
// class instance to handle an interrupt
void bTrigger::handleInterrupt() {
  lastTriggerTime = millis();
  counter_++;
}

////////////////////////////////////////////////////////////////////
// TrialTrigger
//	Start running=off and then toggle running (on->off->on-->off) on every change of a pin
////////////////////////////////////////////////////////////////////
class TrialTrigger : public bTrigger {
  public:
    TrialTrigger(const byte whichISR); //ISR is (0,1), it is not a pin
    virtual void handleInterrupt();
    boolean isRunning() { return isRunning_; } 
  private:
  	boolean isRunning_;
  	unsigned long lastOnTime_;
  	unsigned long lastOffTime_;
};

TrialTrigger::TrialTrigger(const byte whichISR) : bTrigger(whichISR) {
	isRunning_ = false;
	lastOnTime_ = 0;
	lastOffTime_ = 0;
}
//any time the trigger changes, we flip between running and not running
void TrialTrigger::handleInterrupt() {
	bTrigger::handleInterrupt();
	isRunning_ = ! isRunning_;
	if (isRunning_) {
		lastOnTime_ = getLastTime();
	} else {
		lastOffTime_ = getLastTime();
	}
}

////////////////////////////////////////////////////////////////////
// FrameTrigger
////////////////////////////////////////////////////////////////////
const int kMaxFrames = 9000;

class FrameTrigger : public bTrigger {
  public:
    FrameTrigger(const byte whichISR); //ISR is (0,1), it is not a pin
    virtual void handleInterrupt();
    void serialPrint();
  private:
  	unsigned long frames[kMaxFrames];
};

FrameTrigger::FrameTrigger(const byte whichISR) : bTrigger(whichISR) {
}
//any time the trigger changes, we flip between running and not running
void FrameTrigger::handleInterrupt() {
	bTrigger::handleInterrupt();
	frames[getCount()-1] = getLastTime();
}
//
void FrameTrigger::serialPrint() {
	int i;
	for (i=0; i<getCount(); i++) {
		Serial.println(String(i) + "," + String(frames[i]));
	}
}

/////////////////////////////////////////////////////////////////////
class Experiment {
	public:
		Experiment();
		void setup();

		TrialTrigger trialTrigger;
		FrameTrigger frameTrigger; //frame clock is actually simplest possible trigger
	
};

Experiment::Experiment() : trialTrigger(0), frameTrigger(1){
	//trialTrigger(0);
	//frameTrigger(1);	
}
void Experiment::setup() {
  trialTrigger.begin(CHANGE); 
  frameTrigger.begin(RISING); 
}

/////////////////////////////////////////////////////////////////////
// User code
/////////////////////////////////////////////////////////////////////


Experiment myExperiment();

int triggerPin = 2;
int framePin = 3;
int ledPin = 13;
bSimulateScope fakeScope(triggerPin, framePin, ledPin);

void setup() {
	Serial.begin(115600);

	myExperiment.setup();
}

unsigned long now;
String inString;
boolean serialHandled;

void loop() {
	now = millis();
	
	if (Serial.available() > 0) {
		inString = Serial.readStringUntil('\n');
		serialHandled = fakeScope.SerialIn(now, inString);
	}
	
	fakeScope.Update();

	
}
