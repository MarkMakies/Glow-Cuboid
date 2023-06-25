###############################################################################
# 8x8 NeoPixel matrix.  using ramp program in LED boy as basis
# GlowBit libraries really slow for this app, so using NeoPixel (7x faster)
#
# v1.01 added network, MQTT 
# v1.02 about to remove network and go back to pico zero
# v1.03 new case, new unbroken matrix, add two additional modes

version = '1.03'

print('Glow Cube on RP2040-Zero, v' + version)
print('Mark Makies, Apr 2023')

from machine import Pin, SoftI2C
from time import sleep_ms, ticks_ms
import random
from random import randint as RI

import gc
import neopixel
import mpu6050

i2c = SoftI2C(scl=Pin(1), sda=Pin(0), freq=320_000)
mpu= mpu6050.accel(i2c)
mpu_ticks = ticks_ms()

numPixels = 64
NeoPin = Pin(14,Pin.OUT)                        # built in LED on pin 16
Neo = neopixel.NeoPixel(NeoPin,numPixels)

MinLevel = 4
MaxLevel = 15

###############################################################################
# Lights Action
# Type A: random slopes and levels, assigned to a finite number of pixels
#         only 2 of 3 pixel LEDs on at any one time
#         cable entry from left side
#
# Type B: from initial LED Boy / Light House ramp but rather than per pixel, 
#         these are randomly mapped spacially.  random element for timing,
#         pixel deletion, and random pixels
#         cable entry from bottom
#
# Type R: Random
#         cable entry from right side
#
# Type S: Random with a weighting to try to promote symbol like patterns
#         cable entry from top

Type = 'A'

LoopTime = 50 #ms
ResetState1 = True
ResetState2 = True

def NNcount(i):
    row = i // 8
    col = i % 8
    n = 0

    if 0 < row < 7 and 0 < col < 7:                     # all middle section
        n = (ON[i-1] + ON[i+1] + ON[i-8] + ON[i+8] + 
             ON[i-9] + ON[i-7] + ON[i+7] + ON[i+9])

    elif row == 0 and 0 < col < 7:                      # top row (no corners)
        n = ON[i-1] + ON[i+1] + ON[i+8] + ON[i+7] + ON[i+9]
    elif row == 7 and 0 < col < 7:                      # bottom row (no corners)
        n = ON[i-1] + ON[i+1] + ON[i-8] + ON[i-9] + ON[i-7]
    
    elif col == 0 and 0 < row < 7:                      # first column (no corners)
        n = ON[i-8] + ON[i+8] + ON[i+1] + ON[i-7] + ON[i+9]
    elif col == 7 and 0 < row < 7:                      # last column (no corners)
        n = ON[i-8] + ON[i+8] + ON[i-1] + ON[i+7] + ON[i-9]

    elif col == 0 and row == 0:                         # top left corner
        n = ON[i+8] + ON[i+1] + ON[i+9]    
    elif col == 7 and row == 0:                         # top right corner
        n = ON[i+8] + ON[i-1] + ON[i+7]   

    elif col == 0 and row == 7:                         # bottom left corner
        n = ON[i-8] + ON[i+1] + ON[i-7]    
    elif col == 7 and row == 7:                         # bottom right corner
        n = ON[i-8] + ON[i-1] + ON[i-9] 

    return n

def Run4(t0,t1,t2,t3,t4,t5,t6,t7,t8, prob): 
    searching = True
    StartTime = ticks_ms()

    while searching:
        for k in range(numPixels):
            t = RI(1,100)
            if t < prob:
                R[k] = RI(0, MaxLevel - 2)
                G[k] = RI(0, MaxLevel + 7)
                B[k] = RI(0, MaxLevel)
                
                aa = RI(1,3)
                if aa == 1:
                    R[k] = 0
                elif aa == 2:
                    G[k] = 0
                else:
                    B[k] = 0

                ON[k] = True
            else:
                R[k] = 0
                G[k] = 0
                B[k] = 0
                ON[k] = False
        
        for k in range(numPixels):
            if ON[k]:
                NN[k] = NNcount(k)          
            else:
                NN[k] = 0

        if (NN.count(0) >= t0 and NN.count(1) >= t1 and NN.count(2) >= t2 and NN.count(3) >= t3 and
                NN.count(4) >= t4 and NN.count(5) >= t5 and NN.count(6) >= t6 and NN.count(7) >= t7 and
                NN.count(8) >= t8):
                # transition

            Ndone = 0 
            while Ndone != 3 * numPixels:
                
                Ndone = 0  
                for k in range(numPixels):
                    rr, gg, bb = Neo[k]
                    
                    if rr > R[k]:
                        rr -= 1
                    elif rr < R[k]:
                        rr += 1
                    else:
                        Ndone += 1

                    if gg > G[k]:
                        gg -= 1
                    elif gg < G[k]:
                        gg += 1                        
                    else:
                        Ndone += 1

                    if bb > B[k]:
                        bb -= 1
                    elif bb < B[k]:
                        bb += 1
                    else:
                        Ndone += 1
                   
                    Neo[k] = (rr, gg, bb)           
            
                neopixel.NeoPixel.write(Neo)
                sleep_ms(RI(10,100))

            searching = False

        if ticks_ms() - StartTime > 1000:       # allow time for main loop to accept input
            searching = False

while True:    
    ss = ticks_ms()

    if Type == 'A':
        ###############################################################################
        # Type A - Loop time around 27ms - pad out to LoopTime
        
        if ResetState1:
            ResetState1 = False
            
            numOff = 37
            MaxBrightMin, MaxBrightMax = MinLevel, MaxLevel         #50ms loop
            ToffMin, ToffMax =  10, 500 
            TonMin, TonMax =    10,100
            TriseMin, TriseMax = 40, 500
            TfallMin, TfallMax = 40, 500

            LEDs =      [[0,0,0] for n in range(numPixels)]
            MaxBright = [[0,0,0] for n in range(numPixels)]
            Toff =      [[0,0,0] for n in range(numPixels)]
            Ton =       [[0,0,0] for n in range(numPixels)]
            Trise =     [[0,0,0] for n in range(numPixels)]
            Tfall =     [[0,0,0] for n in range(numPixels)]
            Count =     [[0,0,0] for n in range(numPixels)]
            RState =    [['ready','ready','ready'] for n in range(numPixels)]
            PState =    ['off' for n in range(numPixels)]

            for k in range(numPixels):
                Neo[k] = ((0, 0, 0))
            neopixel.NeoPixel.write(Neo)

        while PState.count('off') >=  numOff: 	#then fire one up
            jj = RI(0, numPixels-1)
            if PState[jj] == 'off':          
                PState[jj] = 'on'
                break

        for k in range(numPixels):
            if PState[k] == 'on' or PState[k] == 'wait':

                if RState[k].count('ready') > 1 and PState[k] != 'wait': # then fire one up
                    #j = RI(0,2)
                    jjj = random.random() * 100
                    if jjj < 35:
                        j = 0               #red 35%
                    elif jjj < (35+34):
                        j = 1               #green 34%
                    else:
                        j = 2               #blue 31%

                    if RState[k][j] == 'ready':
                        MaxBright[k][j] = RI(MaxBrightMin, MaxBrightMax)
                        Toff[k][j] = RI(ToffMin,ToffMax)
                        Ton[k][j] = RI(TonMin,TonMax)
                        Trise[k][j] = RI(TriseMin,TriseMax)
                        Tfall[k][j] = RI(TfallMin,TfallMax) 
                        
                        Count[k][j] = Toff[k][j]
                        RState[k][j] = 'off'

                for i in range(3):  
                    if RState[k][i] == 'off':
                        if Count[k][i] == 0:    # transition to rising
                            RState[k][i] = 'rising'
                            Count[k][i] = Trise[k][i]
                        else:
                            Count[k][i] -= 1

                    elif RState[k][i] == 'rising':
                        LEDs[k][i] = int(MaxBright[k][i] * (Trise[k][i] - Count[k][i]) / Trise[k][i])
                        if LEDs[k][i] >= MaxBright[k][i]:  # next RState
                            LEDs[k][i] = MaxBright[k][i]
                            RState[k][i] = 'on'
                            Count[k][i] = Ton[k][i]
                        else:
                            Count[k][i] -= 1    
    
                    elif RState[k][i] == 'on':
                        if Count[k][i] == 0:    # transition to falling
                            RState[k][i] = 'falling'
                            Count[k][i] = Tfall[k][i]
                        else:
                            Count[k][i] -= 1

                    elif RState[k][i] == 'falling':    
                        LEDs[k][i] = int(MaxBright[k][i] *  Count[k][i] / Tfall[k][i])
                        if LEDs[k][i] <= 0:
                            LEDs[k][i] = 0
                            RState[k][i] = 'ready'
                            if PState[k] == 'on':
                                PState[k] = 'wait'
                        else:
                            Count[k][i] -= 1      
                if PState[k] == 'wait' and RState[k].count('ready') == 3:
                    PState[k] = 'off'

                R = int(LEDs[k][0])
                G = int(LEDs[k][1])
                B = int(LEDs[k][2])

                Neo[k] = (R,G,B)

        neopixel.NeoPixel.write(Neo) # consistant execute time 2.03ms 
        gc.collect()

        elapsed = ticks_ms() - ss
        if elapsed > LoopTime:
            print('Warning, loop taking too long:', elapsed, 'ms')
        else:
            sleep_ms(LoopTime - elapsed)

    elif Type == 'B':
        ###############################################################################
        # Type B loop time 4.5 ms

        if ResetState2:
            ResetState2 = False
       
            ToffMin = 1 
            ToffMax = 2
            TonMin = 2
            TonMax = 70
            TriseMin = 5    
            TriseMax = 30
            TfallMin = 5
            TfallMax = 30

            LEDs = [0,0,0]
            Toff = [0,0,0]  
            Ton = [0,0,0]
            Trise = [0,0,0]   
            Tfall = [0,0,0]
            RState = ['ready','ready','ready']
            Count = [0,0,0]
            rduty = [0,0,0]

            RandTrig = 2 / 100 
            RandOff  = 57 / 100
            RandRand = 7 / 100

            for k in range(numPixels):
                Neo[k] = ((0, 0, 0))
            neopixel.NeoPixel.write(Neo)

        if RState.count('ready') > 1: # then fire one up
            j = RI(0,2)
            if RState[j] == 'ready':
                Toff[j] = RI(ToffMin,ToffMax)
                Ton[j] = RI(TonMin,TonMax)
                Trise[j] = RI(TriseMin,TriseMax)
                Tfall[j] = RI(TfallMin,TfallMax) 
                
                Count[j] = Toff[j]
                RState[j] = 'off'

        for i in range(3):  
            if RState[i] == 'off':
                if Count[i] == 0:    # transition to rising
                    RState[i] = 'rising'
                    Count[i] = Trise[i]
                else:
                    Count[i] -= 1

            elif RState[i] == 'rising':
                if Count[i] == 0:   # ramp up or next RState
                    rduty[i] += 1
                    if rduty[i] > 255:  # next RState
                        rduty[i] = 255
                        RState[i] = 'on'
                        Count[i] = Ton[i]
                    else:
                        Count[i] = Trise[i]
                    LEDs[i] = rduty[i]
                else:
                    Count[i] -= 1    

            elif RState[i] == 'on':
                if Count[i] == 0:    # transition to falling
                    RState[i] = 'falling'
                    Count[i] = Tfall[i]
                else:
                    Count[i] -= 1

            elif RState[i] == 'falling':    
                if Count[i] == 0:   # step down or out
                    rduty[i] -= 1
                    if rduty[i] < 0:
                        rduty[i] = 0
                        RState[i] = 'ready'
                    else:
                        Count[i] = Tfall[i]
                    LEDs[i] = rduty[i]
                else:
                    Count[i] -= 1         
        
        t = random.random()
        if t < RandTrig:
            k = RI(0, (numPixels-1))
            R = int(LEDs[0] * MaxLevel / 255)
            G = int(LEDs[1] * MaxLevel / 255)
            B = int(LEDs[2] * MaxLevel / 255)
            Neo[k] = (R,G,B)
                            
            t = random.random()
            if t < RandOff :
                Neo[k] = (0,0,0)
            
            t = random.random()
            if t < RandRand :
                av = int((R + B + G) / 3)
                R = RI(0, av)
                G = RI(0, av - R)
                B = RI(0, av - R - G)
                Neo[k] = (R,G,B)

            neopixel.NeoPixel.write(Neo)
        gc.collect()

    elif Type == 'R':
        ###############################################################################
        # Type R loop time ? ms

        if ResetState3:
            ResetState3 = False
            for k in range(numPixels):
                Neo[k] = ((0, 0, 0))
            neopixel.NeoPixel.write(Neo)      

        if RI(1, 100) < 50:
            xx = RI(1,3)
            if xx == 1:
                R = 0
            else:
                R = RI(0, MaxLevel)
            if xx == 2:
                G = 0
            else:
                G = RI(0, MaxLevel)
            if xx == 3:
                B = 0
            else:
                B = RI(0, MaxLevel)

        if RI(1, 100) < 50:
            R, G, B = 0, 0, 0
              
        Neo[RI(0, (numPixels-1))] = (R,G,B)
        
        neopixel.NeoPixel.write(Neo)
        sleep_ms(RI(10,100))

        gc.collect()
    
    elif Type == 'S':
        ###############################################################################
        # Type S loop time ? ms

        if ResetState4:
            ResetState4 = False
            R = [0 for n in range(numPixels)]
            G = [0 for n in range(numPixels)]
            B = [0 for n in range(numPixels)]
            ON = [False for n in range(numPixels)]
            NN = [0 for n in range(numPixels)]
            for k in range(numPixels):
                Neo[k] = ((0, 0, 0))
            neopixel.NeoPixel.write(Neo)

        Run4(0,0,12,5,0,0,0,0,0,25)
      
        gc.collect()

    ###########################################################################
    # motion processing
    now = ticks_ms()
    
    if True:
    # if now - mpu_ticks > 100:

        mpu_ticks = now

        thresh = 12_000
        cdelay = 200

        t = mpu.get_values()
        sleep_ms(1)
        t = mpu.get_values()
        ax = t['AcX']
        ay = t['AcY']
        az = t['AcZ']

        if az < -thresh and Type != 'Z':           # on back
            Type = 'Z'
            ResetState1 = True
            ResetState2 = True
            ResetState3 = True
            ResetState4 = True
            sleep_ms(cdelay)
            print('Reset Initiated (Type Z)')

        if ay < -thresh and Type != 'B':          # bottom cable entry
            Type = 'B'
            sleep_ms(cdelay)
            ResetState2 = True
            print('State Change to Type B')

        elif ax > thresh and Type != 'R':          # right cable entry
            Type = 'R'
            sleep_ms(cdelay)
            ResetState3 = True
            print('State Change to Type R')

        elif ay > thresh and Type != 'S':          # top cable entry
            Type = 'S'
            sleep_ms(cdelay)
            ResetState4 = True
            print('State Change to Type S')

        elif ax < -thresh and Type != 'A':          # left cable entry
            Type = 'A'
            sleep_ms(cdelay)
            ResetState1 = True
            print('State Change to Type A')
    
    #print(ticks_ms() - ss)
