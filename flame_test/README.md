# Flame Test

This directory has basic test patterns for the piece.

It interacts directly with the controllers. There are 3 esp32 based controllers, each 
with 10 flame jets.

# Art Net Definition

Each controller expresses 10 devices, which in ArtNet terms are Fixtures.

Each controller is at a single IP address, therefore, there are 3.

Each fixture has two channels.

The first channel is "solonoid", which is 1 (on) or 0 (off). 

The second channel is "valve", which controls the flow. This value is from 0 (off) to 255 (full on).

Note that there are two ways to express "off". Thus is is possible to have the valve full open but the solonoid off, and the solonoid on but the valve is off. This is *intentional* because we wish to support "poofs", that is, having the valve wide open and turning the solonoid open.

Therefore, an artnet packet will generally have 20 channels - 2 bytes for each fixture, 10 fixtures, in order.

The solonoids are in a particular order, which will be described in another document.

Artnet packets are *directed*, because we are worried about these embedded systems not playing nice with broadcast IP packets.

Q: The sequence number *is* used. The ArtNet is flowing over wifi, which has a greater chance of inverting packet order.

Q: ArtNet has a discover protocol. This doesn't use them.

# Tests

The test code is written in python. The code is written to python 3.10-ish which is common
around the time we are writing. Likely it is all tested with python 3.11 or 3.12

To add a new test pattern, write it as per the examples. Generally, you'll update the two arrays which
have the flow values (valve), and whether the nozzle is active (solonoid)

# multithreading (higher frame rates)

In order to make up for lost packets, it is better to have a background thread transmit the UDP packets.
This means instead of transmitting and setting a delay, you'd just update the byte array, and the
background thread would continually send. While this could introduce "tearing" and we might then
need to introduce a mutex or think a little about the GIL

(to be implemented)

# TODOs

I hate the syntax of VALVE and ACTIVE. At least, if we use active, we could use a Boolean for better expressiveness.

Should switch the definition from inside the file itself to a JSON. That'll allow easy changing of IP addresses
and/or ranges