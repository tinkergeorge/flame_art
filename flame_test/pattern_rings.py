#!/usr/bin/env python3

# Author: Eric Gauderman

# want the globals and helper functions from flametest
import flame_test as ft
from time import sleep

lower_star = [0, 1, 2, 3, 4]
lower_diagonal = [5, 6, 7, 8, 9]
middle_ring = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
upper_diagonal = [20, 21, 22, 23, 24]
upper_star = [25, 26, 27, 28, 29]
sleep_between = 0.15

def pattern_rings(xmit: ft.LightCurveTransmitter, recv: ft.OSCReceiver):
    print(f'Starting rings pattern')
    xmit.fill_solenoids(0)
    xmit.fill_apertures(1.0)

    index = 0

    for reps in range(5):
        for i in range(len(lower_star)):
            xmit.solenoids[lower_star[i]] = 1
        sleep(sleep_between)

        for i in range(len(lower_star)):
            xmit.solenoids[lower_star[i]] = 0
        for i in range(len(lower_diagonal)):
            xmit.solenoids[lower_diagonal[i]] = 1
        sleep(sleep_between)

        for i in range(len(lower_diagonal)):
            xmit.solenoids[lower_diagonal[i]] = 0
        for i in range(len(middle_ring)):
            xmit.solenoids[middle_ring[i]] = 1
        sleep(sleep_between)

        for i in range(len(middle_ring)):
            xmit.solenoids[middle_ring[i]] = 0
        for i in range(len(upper_diagonal)):
            xmit.solenoids[upper_diagonal[i]] = 1
        sleep(sleep_between)

        for i in range(len(upper_diagonal)):
            xmit.solenoids[upper_diagonal[i]] = 0
        for i in range(len(upper_star)):
            xmit.solenoids[upper_star[i]] = 1
        sleep(sleep_between)

        for i in range(len(upper_star)):
            xmit.solenoids[upper_star[i]] = 0

    xmit.fill_solenoids(0)
    sleep(0.3)
    print(f'Ending rings pattern')
