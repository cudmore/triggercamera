
# Minimized

<IMG SRC="../img/triggercamera-minimized.png" WIDTH=450 style="border:1px solid gray">

# Maximized

<IMG SRC="../img/triggercamera-maximized.png" WIDTH=450 style="border:1px solid gray">

# Interface

## Top

Feedback on the state of the Trigger Camera including if it is running or not, current frame, and current output file. The date and time are from the Raspberry Pi, when the camera is connected, the time will update.

The spinner-icon will animate and the 'frame' will increment when the camera has been triggered and is acquiring video.

## Plot

Plot button to generate a plot of the last trial. This plot shows the interval between frames received and should be used to verify that frame triggering is working as expected.

## Options

Displays the current camera and system configuration. This includes camera frames-per-second (fps) and image size. This also includes the GPIO pin numbers for trigger and frame. In the future, this section will be editable to change these parameters. For now, the software needs to be stopped, config.ini edited and then the software should be restarted.
