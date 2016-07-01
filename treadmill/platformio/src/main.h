//main.h

struct trial
{
   int trialNumber;
   int trialStartMillis;
};

typedef struct trial Trial;

struct steppermotor
{
   int isOn;
   int movePin;
   int dirPin;
};

typedef struct steppermotor StepperMotor;