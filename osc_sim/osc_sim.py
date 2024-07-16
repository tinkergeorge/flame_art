#!/usr/bin/env python3

# this test module sends OSC packets that would simulate
# what we expect the IMU to send

# https://docs.google.com/document/d/1OyvInZ4yD63il6pFvKUpxE_5A0A4D1BgE_5zifzlJRg/edit?usp=sharing

# in short, we'll pack the OSC into UDP broadcast packets. They will look like:
# /LC/gyro ,fff x.x, y.y, z.z
# /LC/rotation
# /LC/gravity

# where
# Rotational Vector: absolute rotational position compared to a fixed reference frame
#   ( what should we do about calibration? )
# Gyroscope: rotational speed around x,y,z (this probably needs no calibration)
# Gravity: used to determine orientiation



# using osc4py 3 as the first attempt
# https://github.com/Xinne/osc4py3
# docs
# https://osc4py3.readthedocs.io/en/latest/index.html

# Each entity will be in a single 

# Author: brian@bulkowski.org Brian Bulkowski 2024 Copyright assigned to Sam Cooler

from time import sleep, time
import argparse
from threading import Thread, Event
import math

from osc4py3.as_eventloop import *
from osc4py3 import oscbuildparse

import netifaces

import os
import sys


OSC_PORT = 6511 # a random number. there is no OSC port because OSC is not a protocol

debug = False
ARGS = None

# returns a list of the IPv4 broadcast strings

def get_broadcast_addresses():
    interfaces = netifaces.interfaces()
    interface_broadcasts = []

    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ipv4_info = addresses[netifaces.AF_INET][0]
            broadcast_address = ipv4_info.get('broadcast')
            if broadcast_address:
                interface_broadcasts.append(broadcast_address)

    print(f'broadcast addresses are: {interface_broadcasts}')
    return interface_broadcasts

class OSCTransmitter:

    def __init__(self, args) -> None:

        # rotational speed around pitch, yaw, roll        
        self.gyro = [0.0] * 3
        # absolute rotational position compared to a fixed reference frame
        self.rotation = [0.0] * 3
        # the direction in which gravity currently is
        self.gravity = [0.0] * 3

        self.debug = debug
        self.sequence = 0
        self.repeat = args.repeat

        # init the osc system
        osc_startup()

        # this is what unicast looks like
        # osc_udp_client("192.168.0.4",  OSC_PORT, 'client')

        if args.address == "" :

            addresses = get_broadcast_addresses()
            # this is what broadcast looks like
            for a in addresses:
                # don't send on loopback?
                if a != '127.255.255.255':
                    args.address = a
                    break

        osc_udp_client(args.address,  OSC_PORT, 'client')
        print(f'sending broadcast on {args.address}')




    # call repeatedly from the thread to transmit 
    def transmit(self) -> None:

        print(f'transmit') if self.debug else None

        msg_gyro = oscbuildparse.OSCMessage('/LC/gyro', ',fff', self.gyro)
        msg_rotation = oscbuildparse.OSCMessage('LC/rotation', ',fff', self.rotation)
        msg_gravity = oscbuildparse.OSCMessage('/LC/gravity', ',fff', self.gravity)

        #osc_send([msg_gyro, msg_rotation, msg_gravity], 'client' )
        osc_send(msg_gyro, 'client')
        osc_send(msg_rotation, 'client')
        osc_send(msg_gravity, 'client')

        osc_process()


    def fill_gyro(self, val: float):
        for i in range(0,self.gyro):
            self.gyro[i] = val

    def fill_rotation(self, val: int):
        for i in range(0,self.rotation):
            self.rotation[i] = val

    def fill_gravity(self, val: int):
        for i in range(0,self.graviy):
            self.gravity[i] = val

    def print_gyro(self):
        print(self.gyro)

    def print_rotation(self):
        print(self.rotation)

    def print_gravity(self):
        print(self.gravity)

# background 


def xmit_thread(xmit):
    while True:
        osc_process()
        sleep(0.01)

def xmit_thread_init(xmit):
    global BACKGROUND_THREAD, xmit_event
    BACKGROUND_THREAD = Thread(target=xmit_thread, args=(xmit,) )
    BACKGROUND_THREAD.daemon = True
    BACKGROUND_THREAD.start()


def pattern_rotate_all(xmit: OSCTransmitter):

    # full rotation
    steps = 200
    secs = 3.0

    # one rotation in N secs on X axis
    xmit.gyro[0] = 1 / secs
    for i in range(steps):
        xmit.rotation[0] += 1.0 / steps
        sleep(secs / steps)
    xmit.gyro[0] = 0.0
    xmit.rotation[0] = 0.0


    # one rotation in N secs on Y axis
    xmit.gyro[1] = 1 / secs
    for i in range(steps):
        xmit.rotation[1] += 1.0 / steps
        sleep(secs / steps)
    xmit.gyro[1] = 0.0
    xmit.rotation[1] = 0.0

    # one rotation in N secs on Z axis
    xmit.gyro[2] = 1 / secs
    for i in range(steps):
        xmit.rotation[2] += 1.0 / steps
        sleep(secs / steps)
    xmit.gyro[2] = 0.0
    xmit.rotation[2] = 0.0

    # same on all
    # one rotation in N secs on X axis
    xmit.fill_gyro(1 / secs)
    for i in range(steps):
        xmit.fill_rotation( xmit.rotation[0] + (1.0 / steps) )
        sleep(secs / steps)
    xmit.fill_gyro(0.0)
    xmit.fill_rotation(0.0)



#
#

def args_init():
    parser = argparse.ArgumentParser(prog='osc_sim', description='Send packets in the format we expect to drive the flame system')

    parser.add_argument('--address', '-a', default="", type=str, help=f'the multicast IP address to send to')
    parser.add_argument('--pattern', '-p', default="rotate_all", type=str, help=f'pattern one of: rotate_all')
    parser.add_argument('--repeat', '-r', default=1, type=int, help="number of times to run pattern")

    args = parser.parse_args()

    return args


# inits then pattern so simple

def main():

    global ARGS

    args = args_init()

    xmit = OSCTransmitter(args)

    xmit_thread_init(xmit)

    if args.pattern == 'rotate_all':
        pattern_rotate_all(xmit)
    else:
        print(f'pattern must be rotate_all not {args.pattern}')



# only effects when we're being run as a module but whatever
if __name__ == '__main__':
    main()
