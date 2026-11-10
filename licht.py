import RPi.GPIO as GPIO
import time
# CONFIG
BUTTON_PIN = 6
LED_SWITCH_PIN = 13
led_state = False

# GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_SWITCH_PIN, GPIO.OUT)
GPIO.output(LED_SWITCH_PIN, GPIO.HIGH)

# PROZESS
try: 
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            led_state = not led_state
            GPIO.output(LED_SWITCH_PIN, GPIO.HIGH if led_state else GPIO.LOW)
            
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.01)
                
            time.sleep(0.02)
except KeyboardInterrupt:
    GPIO.cleanup()
        
