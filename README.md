## CircuitPythonNeopixels

This repository is setup to deploy a CircuitPython project onto an Adafruit ItsyBitsy Express board to control NeoPixel lights.

### Deploying code

- Connect the board via usb
- If the device shows up as something other than the d: drive, update deploy.ps1 with the right drive letter
- Run the build task in vscode (short-cut `ctrl-shift-b`), this will copy the files over to the device