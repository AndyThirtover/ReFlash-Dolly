import chipdrive
import logging
import time
import yaml
import os.path
from collections import OrderedDict

trinamic_config_file = "trinamic_config.yaml"
journey_config_file = "journey.yaml"
config = {}

nema17={
    'stepsPerRev': 200,       #  No gearbox
    'maxrpm'     : 1200       #  Max Speed
}

mot = chipdrive.tmc5130(settings=nema17,loglvl=logging.ERROR)

thread_data = {'count' : 0,
                'volts' : 0,
                'current_limit' : 0,
                'speed' : 0,
                'A1' : 0,
                'V1' : 0,
                'AMAX' : 0,
                'VMAX' : 0,
                'DMAX' : 0,
                'D1' : 0,
                'DistRev' : 0,
                'mm_per_step' : 0,
                'estimated_pos' : 0,
                'state' : 0,
                'command_current' : 0,
                'measured_current' : 0,
                'dynamic_pos' : 0,
                'dynamic_wait' : 0,
                'rotation_velocity' : 0,
                'idle' : 0
            }

def write_trinamic_config(filename):
    print ("TRINAMIC CONFIG DUMP: {0}".format(config))
    rfile = open(filename,'w')
    rfile.write(yaml.dump(config))
    rfile.close()

def read_trinamic_config(filename):
    global config
    if os.path.isfile(filename):
        with open (filename, 'r') as cfgfile:
            config = yaml.load(cfgfile)
    else:
        # no file found - write default condig values
        config['A1'] = {'120'}
        config['V1'] = {'4000'}
        config['AMAX'] = {'500'}
        config['VMAX'] = {'80000'}
        config['DMAX'] = {'500'}
        config['D1'] = {'120'}
        config['DistRev'] = {'80'}
        write_trinamic_config(filename)
    for key,value in config.items():
        thread_data[key] = value
    config['mm_per_step'] = float(config['DistRev'])/(int(mot.settings['stepsPerRev'])*int(mot.uSC))
    thread_data['mm_per_step'] = config['mm_per_step']

read_trinamic_config(trinamic_config_file)

def process_trinamic_config(formargs):
    global config
    #for key, value in formargs.iteritems():
    for key, value in formargs.items():
        if 'submit' in key:
            pass
        else: 
            print ("Key: {0} Value {1}".format(key,value))
            config[key] = value
            thread_data[key] = value
    write_trinamic_config(trinamic_config_file)

print("Trinamic Config at start: {0}".format(config))

def save_journey(message):
    message = dict(message)
    jfile = open(journey_config_file,'w')
    jfile.write(yaml.dump(message))
    jfile.close()

def load_journey(jfile_name=journey_config_file):
    if os.path.isfile(jfile_name):
        with open(jfile_name,'r') as jfile:
            jdata = yaml.load(jfile)
    return jdata


def set_speed(speedval):
    #
    #   Most of this stuff is set by config
    #
    if int(speedval) > int(thread_data['VMAX']):
        speedval = thread_data['VMAX']

    regsettings=OrderedDict((
        ('A1', int(config['A1'])),
        ('V1', int(config['V1'])),
        ('AMAX', int(config['AMAX'])),
        ('VMAX', int(speedval)),
        ('DMAX', int(config['DMAX'])),              # Deceleration 
        ('D1', int(config['D1']))
         ))
    regactions='WWWWWW'
    assert len(regsettings)==len(regactions)
    currently=mot.md.readWriteMultiple(regsettings,regactions)


def move_to(pos):
    mot.async_goto(pos)

def trajectory_to(to_pos,speed=None):
    print ("TRAJECTORY TO: {} and SPEED: {}".format(int(to_pos),speed))
    print("MicroSteps: {} DistRev: {} mm_per_step: {}".format(mot.uSC,config['DistRev'],config['mm_per_step']))
    # in mm
    to_target = float(to_pos) / config['mm_per_step']
    print("to_target: {}".format(to_target))
    if speed:
        set_speed(speed)
    thread_data['idle'] = 0 # update UI because this automatically enables the motor
    #mot.async_goto(float(to_pos)) # this is the rev version.
    mot.md.enableOutput(True)
    mot.md.writeInt('XTARGET',int(to_target))


def get_motor_data():
    global thread_data
    thread_data['estimated_pos'] = mot.md.readInt('XACTUAL')
    thread_data['speed'] = mot.md.readInt('VACTUAL')
    thread_data['AMAX'] = mot.md.lastwritten['AMAX']
    thread_data['state'] = mot.md.status

def stop_motor():
    mot.stop()

def set_state(state='IDLE'):
    if (state == 'IDLE'):
        mot.md.enableOutput(False)
        thread_data['idle'] = 1
    else:
        mot.md.enableOutput(True)
        thread_data['idle'] = 0
