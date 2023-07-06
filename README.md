# Glow Cuboid
<img src="https://github.com/MarkMakies/Glow-Cube/assets/105891859/68a5bb0c-a1b3-4fde-a600-e47d4d5de3b6" width=50% height=50%>

**Glow Cuboid with 64 LED RGB matrix** 

## Videos of different modes:
- Symbol https://youtu.be/7jHFOrDojFA
- Type A https://youtu.be/Bh6ZJeXqZyo
- Type B https://youtu.be/XRGPs1mgesw
- Random  https://youtu.be/dqcW-FjIBPw

## What does it do?
Not much.  Sixty-four pixels change colour in random patterns and they look good (see videos).  There are 4 modes to choose from.

## How does it work?  
Easy.  It’s just an RP2040 programmed in Python to produce random patterns on an 8x8 RGB LED matrix.   I just played around with numbers and algorithms until I liked the look of them.  It seems that people all have very differing favorites and some that I didn’t like, others love.  So to that end, I created 4 different algorithms which create distinctive patterns over time.   I didn’t want to use any switches so an accelerometer determines the orientation of the cube which sets the mode.  The unit resets itself when put on its back.  

Basically you just plug it in to a USB power source and it does its thing.  Two of the modes take some time to initialise.

The size of the unit was determined by a piece of sample frosted acrylic lying around that measured 100 x 100 x 10mm.

## Parts

- RP2040-Zero, a Pico-like MCU Board Based on Raspberry Pi RP2040
- GlowBit™ Matrix - 8x8
- MPU-6050 Module 3 Axis Gyroscope + Accelerometer
- USB-C cable
- 3D printed front and back pieces, FreeCAD design files, step models and Prusa project files all here
- Acrylic frosted slab, 100x100x10, or anything that is opaque 
