## How to use PlatformIO

```
sudo pip install platformio #one time install

platformio init --board teensy31

platformio run --target upload

platformio run --target clean

platformio serialports monitor -p /dev/ttyACM0 -b 115200 #a serial port monitor
```
