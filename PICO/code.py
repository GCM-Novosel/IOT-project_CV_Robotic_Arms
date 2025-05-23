import time
import board
import pwmio
import digitalio
import wifi
import socketpool
import ssl
import json
import os
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# LED for feedback
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def blink(times, delay=0.1):
    for _ in range(times):
        led.value = True
        time.sleep(delay)
        led.value = False
        time.sleep(delay)

# Servo setup on GP7–GP11
finger_order = ["middle", "ring", "index", "pinkie", "thumb"]
finger_to_pin = {
    "middle": board.GP7,
    "ring": board.GP8,
    "index": board.GP9,
    "pinkie": board.GP10,
    "thumb": board.GP11
}
servos = {
    name: pwmio.PWMOut(pin, frequency=50)
    for name, pin in finger_to_pin.items()
}

# Optional angle limits
finger_limits = {
    "thumb": (0, 120)  # Limit thumb range
}

def set_servo_angle_named(finger, pwm, angle):
    min_a, max_a = finger_limits.get(finger, (0, 180))
    angle = max(min_a, min(max_a, angle))  # Clamp
    min_duty = 2 ** 16 * 0.03  # 1 ms
    max_duty = 2 ** 16 * 0.12  # 2 ms
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    pwm.duty_cycle = duty


# Connect to Wi-Fi
wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))

# MQTT setup
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()

mqtt_client = MQTT.MQTT(
    broker=os.getenv("MQTT_BROKER"),
    port=int(os.getenv("MQTT_PORT")),
    username=os.getenv("MQTT_USERNAME"),
    password=os.getenv("MQTT_PASSWORD"),
    socket_pool=pool,
    ssl_context=ssl_context,
)

def on_connect(client, userdata, flags, rc):
    for finger in finger_order:
        topic = f"/v1.6/devices/orangepi/{finger}"
        mqtt_client.subscribe(topic)

def on_message(client, topic, message):
    try:
        data = json.loads(message)
        finger = topic.split("/")[-1]
        angle = int(data["value"])
        if finger in servos:
            set_servo_angle_named(finger, servos[finger], angle)
            blink(1, 0.01)
    except Exception as e:
        blink(3, 0.05)

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect()
blink(3)

# Main loop
while True:
    try:
        mqtt_client.loop()
    except Exception as e:
        blink(10, 0.05)
        time.sleep(2)
        try:
            mqtt_client.reconnect()
        except:
            pass
