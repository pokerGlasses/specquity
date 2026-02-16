import RPi.GPIO as GPIO

BTN_CAPTURE = 17
BTN_RESET = 22

class PokerState:
    def __init__(self, capture_callback, reset_callback):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BTN_CAPTURE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BTN_RESET, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Link the buttons to the main orchestrator functions
        GPIO.add_event_detect(BTN_CAPTURE, GPIO.FALLING, callback=capture_callback, bouncetime=500)
        GPIO.add_event_detect(BTN_RESET, GPIO.FALLING, callback=reset_callback, bouncetime=500)

    def cleanup(self):
        GPIO.cleanup()