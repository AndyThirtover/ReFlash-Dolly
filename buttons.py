import threading
import time
import urllib
import yaml
import os.path


TESTING = True

#
#  Handle Buttons, for enable/disable etx
#
import pigpio
GPIO = pigpio.pi()
# debounce is number of times that sleep_time need to have passed to consider the button pressed.
# keep_out is the time before another button press can be processed.
debounce = 4
sleep_time = 0.05
keep_out = 0.7
button_config_file = "buttons.yaml"


buttons = {}

#GPIO = MagicMock()


def read_button_config(filename):
    global buttons
    if os.path.isfile(filename):
        with open (filename, 'r') as cfgfile:
            buttons = yaml.load(cfgfile)
    else:
        if not buttons.has_key('5'):
            buttons['5'] = {'url':'http://127.0.0.1:5000/command/neo_off', 'debounce':debounce}
        if not buttons.has_key('6'):
            buttons['6'] = {'url':'http://127.0.0.1:5000/command/rotate', 'debounce':debounce}
        write_button_config(filename)

read_button_config(button_config_file)

def process_button_config(formargs):
    global buttons
    for key, value in formargs.iteritems():
        if 'submit' in key:
            pass
        else: 
            print ("Key: {0} Value {1}".format(key,value))
            buttons[key]['url'] = value
    write_button_config(button_config_file)


def write_button_config(filename):
    print ("BUTTON DUMP: {0}".format(buttons))
    rfile = open(filename,'w')
    rfile.write(yaml.dump(buttons))
    rfile.close()



def action(button):
    global buttons
    print ("BUTTON at Pin {0} Activated".format(button))
    try:
        urllib2.urlopen(buttons[button]['url'])
    except:
        print ("FAILED URL: {0}".format(buttons[button]['url']))


def read_button_task(stop_event):
    global buttons
    print("Button Config at start: {0}".format(buttons))
    #GPIO.set_mode(GPIO.BCM)
    for button in buttons:
        GPIO.set_mode(int(button), pigpio.INPUT)
        GPIO.set_pull_up_down(int(button),pigpio.PUD_UP)
    while not stop_event.is_set():
        # Have buttons been pressed.
        for button in buttons:
            if not GPIO.read(int(button)):
                buttons[button]['debounce'] -= 1

            if buttons[button]['debounce'] < 0:
                action(button)
                buttons[button]['debounce'] = debounce
                time.sleep(keep_out)
        time.sleep(sleep_time)
    print("=== Stopping Button Thread ===")


if __name__ == "__main__":
    # Tests
    print("URLs may fail during testing, it's the pin numbers that are important")
    running = threading.Event()
    test_thread = threading.Thread(name="testing", target=read_button_task, args=(running,))
    test_thread.start()
    time.sleep(30)
    running.set()
