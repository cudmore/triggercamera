
# Minimized

<IMG SRC="../img/triggercamera-minimized.png" WIDTH=450 style="border:1px solid gray">

<!-- <IMG SRC="../img/triggercamera-minimized.png" WIDTH=450 style="border:1px solid gray"> -->

The top section of the interface provides feedback on the camera status. When a trial is running and video is being recorded, the spinner will spin and **Elapsed Time**, **Frame**, **Trial**, and **File** will update.

Use the **<font style="color:green">Start Arm</font>** and **<font style="color:red">Stop Arm</font>** buttons to turn the listening for a trigger on and off.

Use the **<font style="color:green">Start Stream</font>** and **<font style="color:red">Stop Stream</font>** buttons to turn real-time video streaming on and off.

If LEDs are wired to the Raspberry Pi, LED1 and LED2 provide an interface to turn them on and off as well as to set their brightness levels.

# Maximized

<IMG SRC="../img/triggercamera-maximized.png" WIDTH=450 style="border:1px solid gray">

<!-- <IMG SRC="../img/triggercamera-maximized.png" WIDTH=450 style="border:1px solid gray"> -->

When maximized, there are additional sections for analysis, options, and simulation of a microscope triggers.

## Analysis

The **Plot Last Trial** button will generate a plot of frame-intervals versus frame number for the last trial. This can be used to verify that frame triggering is working as expected. In this example, the majority of 600 frames had an  interval of 30 ms with 4 bad frames.

Bring up the Analysis page (with the line graph icon) to make the same plot for any trials previously recorded.

## Options

Displays the current camera and system configuration. This includes camera frames-per-second (fps) and image size. This also includes the GPIO pin numbers for trigger and frame.

To change options, manually edit the config.ini file and then 'REload Configuration'.

## Simulate

If configured, will use an Arduino to simulate trial and frame triggers of a microscope. This is useful for debugging the camera.

# Analysis

The analysis web page displays a list of trials that have been acquired with the camera. Double-click on a trial (row) to display the timing of the frames.

<IMG SRC="../img/triggercamera-analysis.png" WIDTH=550 style="border:1px solid gray">

