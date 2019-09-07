import threading
import queue
import logging
import time
import math
import random
import yaml
import numpy


"""
def do_cycle(event,pos,wait):
    event.clear()
    wait = float(wait)
    print ("DO CYCLE CALLED P1:{} P2:{}".format(pos,wait))
    while not event.is_set():
        my_drive.axis0.controller.pos_setpoint = pos
        time.sleep(wait)
        my_drive.axis0.controller.pos_setpoint = 0
        time.sleep(wait)

    my_drive.axis0.controller.pos_setpoint = 0  # ensure at zero for next task
    print("DO CYCLE CLEARED")


def set_dynamic(pos,wait):
    thread_data['dynamic_pos'] = pos
    thread_data['dynamic_wait'] = wait


def dynamic_cycle(event,pos=None,wait=None):
    event.clear()
    print ("DYNAMIC CYCLE CALLED - POS:{} WAIT:{}".format(thread_data['dynamic_pos'], thread_data['dynamic_wait']))
    while not event.is_set():
        wait = float(thread_data['dynamic_wait'])
        my_drive.axis0.controller.pos_setpoint = thread_data['dynamic_pos']
        time.sleep(wait)
        my_drive.axis0.controller.pos_setpoint = 0
        time.sleep(wait)

    my_drive.axis0.controller.pos_setpoint = 0  # ensure at zero for next task
    print("DYNAMIC CYCLE CLEARED")

"""