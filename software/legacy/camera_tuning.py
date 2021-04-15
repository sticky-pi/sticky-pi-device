
import picamera
import logging
import RPi.GPIO as GPIO
import time
import picamera
import optparse

if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option("-D", "--debug", dest="debug", default=False, help="Set DEBUG mode ON", action="store_true")
    parser.add_option("-w", "--width", dest="w", default=2592)
    parser.add_option("-v", "--height", dest="h", default=1944)
    parser.add_option("-r", "--roll", dest="roll", default=False, action='store_true')

    (options, args) = parser.parse_args()
    option_dict = vars(options)

    _resolution = (int(option_dict['w']), int(option_dict['h']))
    _flash_gpio = 19
    logging.info('powering off though gpio')

    GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
    GPIO.setup(_flash_gpio, GPIO.OUT)  # set a port/pin as an output
    cam = None
    try:
        GPIO.output(_flash_gpio, 1)
        cam = picamera.PiCamera()
        cam.resolution = _resolution
#        cam.meter_mode = 'backlit'
        cam.framerate = 10
        cam.exposure_mode = 'backlight'
#        cam.awb_mode = 'off'
#        cam.awb_gains=(1.0,4.0)

#        cam.drc_strength = 'high'
        time.sleep(1)
        cam.iso=100
#        cam.shutter_speed = 12000
        cam.start_preview()
       

        while True:
            if not option_dict['roll']:
                 GPIO.output(_flash_gpio, 1)
                 time.sleep(0.01)
                 cam.zoom= (3/8,3/8, 1/4, 1/4)
                 continue
            for i in [(3/8, 3/8),(0,0), (0, 3/4), (3/4,3/4), (3/4, 0), None]:
                if i is None:
                    cam.zoom= (0,0, 1, 1)
                else:
                    cam.zoom= (i[0],i[1], 1/4, 1/4)
                j=0
                while j < 300: 
                     GPIO.output(_flash_gpio, 1)
                     time.sleep(0.01)
                     j+=1
                   
    finally:
        if cam is not None:
            cam.stop_preview()
        GPIO.output(_flash_gpio, 0)
