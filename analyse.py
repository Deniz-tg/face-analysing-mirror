import RPi.GPIO as GPIO
from picamera2 import Picamera2
from PIL import Image 
import requests
import time

# CONFIG
BUTTON_PIN = 17
LED_SWITCH_PIN = 26
IMG_PATH = "/home/magicmirror/face.jpg"
OUTPUT_PATH = "/home/magicmirror/face_result.txt"

# Face++ API
API_KEY = "KEY"
API_SECRET = "SECRET"
API_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"

# GPIO SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_SWITCH_PIN, GPIO.OUT)
GPIO.output(LED_SWITCH_PIN, GPIO.LOW)


# CAMERA SETUP
camera = Picamera2()
camera.configure(camera.create_still_configuration())

# RESIZE
def resize_image_if_needed(path):
        img = Image.open(path)
        max_size = 1024
        if img.width > 4096 or img.height > 4096:
                print("Bild zu groß, wird verkleinert...")
                ratio = min(max_size / img.width, max_size / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size)
                img.save(path)

# ANALYSE DATEN
def analyze_face(image_path):
        with open(image_path, 'rb') as image_file:
                files = {
                        'image_file': image_file
                }
                data = {
                        'api_key': API_KEY,
                        'api_secret': API_SECRET,
                        'return_attributes': 'skinstatus'
                }
                response = requests.post(API_URL, data=data, files=files)
                print(response.status_code)
                print(response.text)
                return response.json()

# PROZESS
while True:
        try:

                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                        print("📸 Foto wird aufgenommen...")
                        
                        GPIO.output(LED_SWITCH_PIN, GPIO.HIGH)
                        time.sleep(0.2)
                        camera.start()
                        time.sleep(2)
                        camera.capture_file(IMG_PATH)
                        camera.stop()
                        GPIO.output(LED_SWITCH_PIN, GPIO.LOW)
                        print("✅ Foto aufgenommen.")
                        
                        resize_image_if_needed(IMG_PATH)

                        print("📡 Sende Bild zur Analyse...")
                        result = analyze_face(IMG_PATH)

                        skin_data = result.get('faces', [{}])[0].get('attributes', {}).get('skinstatus', {})
                        skin = result["faces"][0]["attributes"]["skinstatus"]
                        
                        output = "Hautanalyse-Ergebnisse:\n"
                        output += "Pflege-Tipps:\n"
                        output += f"Gesundheit: {skin.get('health', 0):.2f}\n"          
                        output += f"Verfärbungen: {skin.get('stain', 0):.2f}\n"
                        output += f"Augenringe: {skin.get('dark_circle', 0):.2f}\n"
                        output += f"Akne: {skin.get('acne', 0):.2f}\n"

                        verbesserungsbedarf = False
                        tipps = ""

                        if skin.get("stain", 0) > 50:
                                tipps += "➤ Flecken sichtbar – verwende aufhellende Pflegeprodukte.\n"
                                verbesserungsbedarf = True
                        if skin.get("dark_circle", 0) > 20:
                                tipps += "➤ Augenringe erkannt – mehr Schlaf & Augencreme empfohlen.\n"
                                verbesserungsbedarf = True
                        if skin.get("acne", 0) > 50:
                                tipps += "➤ Hautunreinheiten – verwende sanfte Anti-Pickel Pflege.\n"
                                verbesserungsbedarf = True
                        if skin.get("health", 0) < 0.5:
                                tipps += "➤ Allgemeine Hautgesundheit gering – intensivere Pflege empfohlen.\n"
                                verbesserungsbedarf = True

                        if verbesserungsbedarf:
                                output += "\n- Hautanalyse zeigt Verbesserungsbedarf!\n"
                                output += tipps
                        else:
                                output += "\n- Alles sieht gut aus! 😊 Weiter so!\n"


                        with open(OUTPUT_PATH, 'w') as file:
                                if skin_data:
                                        file.write(output)

                                else:
                                        file.write("❌ Keine Hautdaten erkannt.\n")

                        print(f"📄 Ergebnisse gespeichert unter {OUTPUT_PATH}")
                        time.sleep(1)


        except Exception:
                with open(OUTPUT_PATH, 'w') as f:
                        f.write("FEHLER: Gesicht nicht erkannt.\n")
                time.sleep(1)
                continue
