
# Minimized

<IMG SRC="../img/triggercamera-minimized2.png" WIDTH=450 style="border:1px solid gray">

<!-- <IMG SRC="../img/triggercamera-minimized.png" WIDTH=450 style="border:1px solid gray"> -->

The top section of the interface provides feedback on the camera status. When a trial is running and video is being recorded, the spinner will spin and **Elapsed Time**, **Frame**, **Trial**, and **File** will update.

Use the **<font style="color:green">Start Arm</font>** and **<font style="color:red">Stop Arm</font>** buttons to turn the listening for a trigger on and off.

If LEDs are wired to the Raspberry Pi, LED1 and LED2 provide an interface to turn them on and off as well as to set their brightness levels.

# Maximized

<IMG SRC="../img/triggercamera-maximized2.png" WIDTH=450 style="border:1px solid gray">

<!-- <IMG SRC="../img/triggercamera-maximized.png" WIDTH=450 style="border:1px solid gray"> -->

# Interface

## Analysis

The **Plot Last Trial** button will generate a plot of frame-intervals versus frame number for the last trial. This can be used to verify that frame triggering is working as expected.

## Options

Displays the current camera and system configuration. This includes camera frames-per-second (fps) and image size. This also includes the GPIO pin numbers for trigger and frame.

In the future, this section will be editable to change these parameters. For now, the software needs to be stopped, config.ini edited and then the software should be restarted.
