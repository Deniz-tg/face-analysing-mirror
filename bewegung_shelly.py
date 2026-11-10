import RPi.GPIO as GPIO
import requests
import time

# CONFIG
PIR_PIN = 18  # OUT-Pin vom Sensor
SHELLY_IP = "IP"  # ← hier deine feste IP vom Shelly Plug S

# GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# METHODS
def schalte_shelly_an():
    print("💡 Shelly AN")
    requests.get(f"http://{SHELLY_IP}/relay/0?turn=on")

def schalte_shelly_aus():
    print("💤 Shelly AUS")
    requests.get(f"http://{SHELLY_IP}/relay/0?turn=off")

print("🚨 Warte auf Bewegung...")

#PROZESS
try:
    while True:
        if GPIO.input(PIR_PIN):
            print("🕴️ Bewegung erkannt!")
            schalte_shelly_an()
            time.sleep(300)  # 5 Minuten warten
            schalte_shelly_aus()
        time.sleep(1)  # 1 Sekunde Pause bevor erneut geprüft wird
except KeyboardInterrupt:
    GPIO.cleanup()
    print("🧹 Aufgeräumt")
