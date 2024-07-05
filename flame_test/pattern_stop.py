#!/usr/bin/env python3

# Author: Brian Bulkowski brian@bulkowski.org

# want the globals and helper functions from flametest
import flame_test as ft
from time import sleep

def pattern_stop(xmit: ft.LightCurveTransmitter):

    print('Shutting down fire')

    # Close all solenoids
    xmit.fill_solenoids(0)
    xmit.fill_apertures(0.0)

    # Dont do this normally!
    # This is a special case where we NEED to know that the information
    # has been sent
    xmit.transmit()

