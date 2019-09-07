#!/usr/bin/python3
"""
TEST trinamic drivers
"""

import chipdrive
import logging
import time
from collections import OrderedDict

nema17={
    'stepsPerRev': 200,       #  No gearbox
    'maxrpm'     : 1200       #  Max Speed
}



mot = chipdrive.tmc5130(settings=nema17,loglvl=logging.ERROR)
time.sleep(0.5)
print("XACTUAL: {}".format(mot.md.readInt('XACTUAL')))


def set_speed(speedval):
    regsettings=OrderedDict((
        ('A1', 12000),
        ('V1', 4000),
        ('AMAX', 20000),
        ('VMAX', speedval),
        ('DMAX', 9000),
        ('D1', 600)
         ))
    regactions='WWWWWW'
    assert len(regsettings)==len(regactions)
    currently=mot.md.readWriteMultiple(regsettings,regactions)


print("TIMED tests on GOTO")

for i in range(2):
    mot.goto(0.3)
    mot.goto(0)

print("DIFFERENCE at ZERO for ASYNC_GOTO")

for i in range(5):
    mot.async_goto(0.3)
    while mot.are_we_there_yet() != 0:
        pass
    mot.async_goto(0)
    while mot.are_we_there_yet() != 0:
        pass

print("ACCELERATION TESTS")

print("Goto position 10")
mot.async_goto(10)
time.sleep(0.5)
print("0.5 We are at: {}".format(mot.are_we_there_yet()))
while mot.are_we_there_yet() != 0:
    time.sleep(0.05)
print("Goto position 0")
mot.async_goto(0)
while mot.are_we_there_yet() != 0:
    time.sleep(0.05)


#Speed Change on the fly
print("SPEED CHANGE TESTS")
print("Set speed to Low")

set_speed(4000)
print("Goto 10")
mot.async_goto(10)
time.sleep(2)

print("ON THE FLY SPEED CHANGE TESTS")
set_speed(16000)
time.sleep(2)
print("Set speed to 32000")
set_speed(32000)
time.sleep(2)
print("Set speed to 64000")
set_speed(64000)
time.sleep(2)
print("Set speed to 256000")
set_speed(256000)


while mot.are_we_there_yet() != 0:
    time.sleep(0.05)

mot.goto(0)  # do we end up in the right place?
print("XACTUAL: {}".format(mot.md.readInt('XACTUAL')))

mot.stop()

