#!/usr/bin/env python3

# Author: chatgpt at the instruction of Sam Cooler as translated into python by BB

# want the globals and helper functions from flametest
import flame_test as ft
from time import sleep

def pattern_wave(xmit: ft.LightCurveTransmitter):

    print('Starting Wave Pattern')
    wait = 0.500

    print('Wave: Close all solenoids')
    # Close all solenoids
    xmit.fill_solenoids(0)
    sleep(wait)

    # Open servos fully
    print('Wave: Open all servos and solenoids')
    xmit.fill_solenoids(1)
    xmit.fill_apertures(1.0)
    sleep(wait)

    # Change servo valve from 100% to 10% and back
    step = .05
    steps = int(1/step)
    wait = 0.300
    for i in range(steps):
        print(f'Wave: open solinoid to {1.0 - (i * step)}')
        xmit.fill_apertures(1.0 - (i * step))
        sleep(wait)

    for i in range(steps):
        print(f'Wave: open solinoid to {i * step}')
        xmit.fill_apertures(i * step)
        sleep(wait)

    # Close solenoids
    print(f'Wave: close solenoids')

    xmit.fill_solenoids(0)

    print('Ending Wave Pattern')

