#!/usr/bin/env python3



# WARNING has syntax that is python 3
# you will see strange looking errors in Python2
# not sure exactly which python is required...

# using the pyartnet module for sending artnet. Might almost
# be easier to hand-code it, it's a very simple protocol

# Because packet might be lost or the wifi might be offline, it's
# important to output a steady stream of packets at a given frame rate.
# use a separate thread for that.

# use another thread for actually changing the values.

# to write a pattern, write 

# see readme for definition of the device

# was going to use the pyartnet library but it's really simple to send packets
# import pyartnet

import socket
from time import sleep
import argparse
import json
from threading import Thread
import math

# filled in by config file
CONTROLLERS = None

# there is a numbering system for the nozzles.
# Each offset of the 30 is a very specific one.

NOZZLES = 0

# this corresponds to the servo flow state - float, 0 to 1
FLOWS = None

# this corresponds to the solenoid - 0 to 1
ACTIVES = None 

# frames per second
FPS = 10

ARTNET_PORT = 6454
ARTNET_UNIVERSE = 0
ARTNET_HEADER_SIZE = 18

DEBUG = False

# artnet packet format: ( 18 bytes )
# 8 bytes header: 'Art-Net0'
# 2 bytes: 00 0x50 (artdmx)
# 2 bytes: proto version 0 0x14
# 1 byte: sequence
# 1 byte: physical
# 2 bytes universe (little endian)
# 2 bytes length big endian
# data

def artnet_packet(universe: int, sequence: int, packet: bytearray ):

    # print(f'Artnet_packet: building') if DEBUG else None

    if len(packet) < 18:
        print(f'Artnet Packet: must provide packet at least 18 bytes long, skipping')
        raise Exception("artnet packet builder: too short input packet")
        return

    # print_bytearray(packet)

    packet[0:12] = b'Art-Net\x00\x00\x50\x00\x14'

    packet[12] = sequence
    packet[13] = 0
    packet[14] = universe & 0xff
    packet[15] = (universe >> 8) & 0xff

    l = len(packet) - ARTNET_HEADER_SIZE
    packet[16] = (l >> 8) & 0xff
    packet[17] = l & 0xff

    # print_bytearray(packet)

SOCK = None
SEQUENCE = 0

# call once to set up 
def transmit() -> None:

    global SEQUENCE, SOCK

    print(f'transmit') if DEBUG else None


    for c in CONTROLLERS:

        # allocate the packet TODO allocate a packet once
        packet = bytearray( ( c['nozzles'] * 2) + ARTNET_HEADER_SIZE)

        # fill in the artnet part
        artnet_packet(ARTNET_UNIVERSE, SEQUENCE, packet)

        # fill in the data bytes
        offset = c['offset']
        for i in range(c['nozzles']):

            # validation. Could make optional.
            if (DEBUG and ( ACTIVES[i+offset] < 0) or (ACTIVES[i+offset] > 1)):
                print(f'active at {i+offset} out of range {ACTIVES[i+offset]} skipping')
                return
            if (DEBUG and (FLOWS[i+offset] < 0.0) or (FLOWS[i+offset] > 1.0)):
                print(f'flow at {i+offset} out of range {FLOWS[i+offset]} skipping')

            if FLOWS[i+offset] < 0.10:
                packet[ARTNET_HEADER_SIZE + (i*2) ] = 0
            else:
                packet[ARTNET_HEADER_SIZE + (i*2) ] = ACTIVES[i+offset]

            packet[ARTNET_HEADER_SIZE + (i*2) + 1] = math.floor(FLOWS[i+offset] * 255.0 )

        # transmit
        if DEBUG:
            print(f' sending packet to {c["ip"]} for {c["name"]}')
            print_bytearray(packet)

        SOCK.sendto(packet, (c['ip'], ARTNET_PORT))

    SEQUENCE = SEQUENCE + 1

def network_init() -> None:

    global SOCK

    # create outbound socket
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    SOCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)



def print_bytearray(b: bytearray) -> None:
    l = len(b)
    o = 0
    while (l > 0):
        if (l >= 8):
            print('{:4x}: {:2x} {:2x} {:2x} {:2x} {:2x} {:2x} {:2x} {:2x}'.format(o, b[o+0],b[o+1],b[o+2],b[o+3],b[o+4],b[o+5],b[o+6],b[o+7]))
            l -= 8
            o += 8
        elif l == 7:
            print('{:4x}: {:2x} {:2x} {:2x} {:2x} {:2x} {:2x} {:2x} '.format(o, b[o+0], b[o+1], b[o+2], b[o+3], b[o+4], b[o+5], b[o+6]))
            l -= 7
            o += 7
        elif l == 6:
            print('{:4x}: {:2x} {:2x} {:2x} {:2x} {:2x} {:2x}'.format(o, b[o+0], b[o+1], b[o+2], b[o+3], b[o+4], b[o+5]))
            l -= 6
            o += 6
        elif l == 5:
            print('{:4x}: {:2x} {:2x} {:2x} {:2x} {:2x}'.format(o, b[o+0], b[o+1], b[o+2], b[o+3], b[o+4] ))
            l -= 5
            o += 5
        elif l == 4:
            print('{:4x}: {:2x} {:2x} {:2x} {:2x}'.format(o, b[o+0], b[o+1], b[o+2], b[o+3] ))
            l -= 4
            o += 4
        elif l == 3:
            print('{:4x}: {:2x} {:2x} {:2x}'.format(o, b[o+0], b[o+1], b[o+2]))
            l -= 3
            o += 3
        elif l == 2:
            print('{:4x}: {:2x} {:2x} '.format(o, b[o+0], b[o+1]))
            l -= 2
            o += 2
        elif l == 1:
            print('{:4x}: {:2x}'.format(o, b[o+0]))
            l -= 1
            o += 1

def fill_flows(val: float):
    global FLOWS
    for i in range(0,NOZZLES):
        FLOWS[i] = val

def fill_actives(val: int):
    global ACTIVES
    for i in range(0,NOZZLES):
        ACTIVES[i] = val

def print_flows():
    print('FLOWS')
    print(FLOWS)

def print_actives():
    print('ACTIVES')
    print(ACTIVES)


def pattern_pulse():

    print(f'Starting Pulse Pattern')

    wait = 1.0

    print(f' Turn on servos and solenoids')
    fill_actives(1)
    fill_flows(1.0)
    transmit()
    sleep(wait)

    # open the valves in steps

    for f in range(0,11):
        print(f' set flow {f / 10.0 }')
        fill_flows(f / 10.0)
        transmit()
        sleep(wait)

    # Close all solenoids, wait, and then close them
    fill_actives(0)
    transmit()
    sleep(wait)

    print(f'Ending Pulse Pattern')


def pattern_wave():

    print('Starting Wave Pattern')
    wait = 0.500

    print('Wave: Close all solenoids')
    # Close all solenoids
    fill_actives(0)
    transmit()
    sleep(wait)

    # Open servos fully
    print('Wave: Open all servos and solenoids')
    fill_actives(1)
    fill_flows(1.0)
    transmit()
    sleep(wait)

    # Change servo valve from 100% to 10% and back
    step = .05;
    steps = int(1/step)
    wait = 0.300;
    for i in range(steps):
        print(f'Wave: open solinoid to {1.0 - (i * step)}')
        fill_flows(1.0 - (i * step))
        transmit()
        sleep(wait)

    for i in range(steps):
        print(f'Wave: open solinoid to {i * step}')
        fill_flows(i * step)
        transmit()
        sleep(wait)

    # Close solenoids
    print(f'Wave: close solenoids')

    fill_actives(0)
    transmit()

    print('Ending Wave Pattern')


def pattern_wave_solenoids():

    period = 0.200

    print(f'Staring wave solenoids pattern')

    # Close all solenoids open all flow
    fill_actives(0)
    fill_flows(1.0)
    transmit()
    sleep(0.100)

    # go through all the solonoids one by one
    for i in range(NOZZLES):
        print(f'turn on solinoid {i}')
        ACTIVES[i] = 1
        transmit()
        sleep(period)

    # close them in the same order
    for i in range(NOZZLES):
        print(f'turn off solinoid {i}')        
        ACTIVES[i] = 0
        transmit()
        sleep(period)

    for i in range(NOZZLES-1,0,-1):
        print(f'turn on solinid {i}')
        ACTIVES[i] = 1
        transmit()
        sleep(period)

    for i in range(NOZZLES-1,0,-1):
        print(f'turn off solinid {i}')
        ACTIVES[i] = 0
        transmit()
        sleep(period)

    print(f'Ending wave solenoids pattern')

# multiwave controls the flows
# have a wave size less than the number of nozzles
# create an array with the pattern
# move the pattern through the nozzles

def pattern_multiwave():

  waveSteps = 20  # Total steps in the wave (up and down), even number
  pattern = [0.0] * waveSteps;

  # Initialize the wave pattern
  for i in range(int(waveSteps / 2)):
    pattern[i] = i / (waveSteps / 2)
    pattern[waveSteps-i-1] = pattern[i]

  print(f'Starting multiwave pattern')

  # Open solenoids close valves
  print(f'open solenoids close valves')
  fill_flows(0.0)
  fill_actives(1)
  transmit()
  sleep(0.100)

  # overlay the pattern
  fill_flows(0.0)
  for i in range(NOZZLES):

    for j in range(waveSteps):
        FLOWS[ (i + j) % len(FLOWS)] = pattern[j]

    print(f'wave offset: {i} shifting: FLOWS')
    print(FLOWS)

    transmit()
    sleep(0.500)

  # Open solenoids close valves
  fill_flows(0.0)
  transmit()

  print(f'Ending multiwave pattern')



def pattern_multipattern():

    print(f'Starting multipattern pattern')

    pattern_pulse()

    pattern_wave()

    pattern_wave_solenoids()

    pattern_multiwave()

    print(f'Ending multipattern pattern')

def arg_init():
    parser = argparse.ArgumentParser(prog='flame_test', description='Send ArtNet packets to the Color Curve for testing')
    parser.add_argument('--host', type=str, help='IP address for destination')
    parser.add_argument('--config','-c', type=str, default="flame_test.cnf", help='Input shrub JSON configuration file')

    parser.add_argument('--pattern', '-p', type=str, help='pulse wave multiwaveone of: pulse, wave, soliwave, multiwave, multipatternpalette, hsv, order, shrub_rank, shrub_rank_order, cube_order, cube_color, black')
    parser.add_argument('--fps', '-f', default=15, type=int, help='frames per second')
    parser.add_argument('--repeat', '-r', default=1, type=int, help="number of times to run pattern")

    global DESTINATION_IP, FPS

    args = parser.parse_args()
    if args.host:
        DESTINATION_IP = args.host
    if args.fps:
        FPS = args.fps

    return args


# inits then pattern so simple

def main():
    args = arg_init()

    network_init()

    # Read configuration file. (They're json files)
    global CONTROLLERS
    with open(args.config) as ftc_f:
        CONTROLLERS = json.load(ftc_f)  # XXX catch exceptions here.

    # base NOZZLES on config file
    global NOZZLES, FLOWS, ACTIVES
    for c in CONTROLLERS:
        NOZZLES = NOZZLES + c['nozzles']
    FLOWS = [0.0] * NOZZLES
    ACTIVES = [0] * NOZZLES

    if not args.pattern:
        for _ in range(args.repeat):
            pattern_pulse()
    elif args.pattern == 'pulse':
        for _ in range(args.repeat):
            pattern_pulse()
    elif args.pattern == 'wave':
        for _ in range(args.repeat):
            pattern_wave()
    elif args.pattern == 'soliwave':
        for _ in range(args.repeat):
            pattern_wave_solenoids()
    elif args.pattern == 'multiwave':
        for _ in range(args.repeat):
            pattern_multiwave()
    elif args.pattern == 'multipattern':
        for _ in range(args.repeat):
            pattern_multipattern()
    else:
        print(' pattern must be one of pulse wave multiwave multipattern')



# only effects when we're being run as a module but whatever
if __name__ == '__main__':
    main()
