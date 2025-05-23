import board
import pwmio
import time
import digitalio

from adafruit_ble import BLERadio
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

# Setup BLE
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)
ble.start_advertising(advertisement)

# LED feedback
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def blink(times, delay=0.1):
    for _ in range(times):
        led.value = True
        time.sleep(delay)
        led.value = False
        time.sleep(delay)

# PWM setup for 5 servos
pwm_pins = [board.GP7, board.GP8, board.GP9, board.GP10, board.GP11]
servos = [pwmio.PWMOut(pin, frequency=50) for pin in pwm_pins]
latest_angles = [90] * 5

def set_servo_angle(pwm, angle):
    angle = max(0, min(180, angle))
    min_duty = 2 ** 16 * 0.05
    max_duty = 2 ** 16 * 0.10
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    pwm.duty_cycle = duty

blink(3)
last_update = time.monotonic()
buffer = ""

while True:
    if not ble.connected:
        ble.start_advertising(advertisement)
        continue

    while ble.connected:
        if uart.in_waiting:
            char = uart.read(1)
            if char == b'\n':
                try:
                    parts = buffer.strip().split(",")
                    if len(parts) == 5:
                        latest_angles = [max(0, min(180, int(p.strip()))) for p in parts]
                        blink(1, 0.05)
                except:
                    blink(10, 0.05)
                buffer = ""
            else:
                buffer += char.decode("utf-8")

        now = time.monotonic()
        if now - last_update >= 0.05:
            for i in range(5):
                set_servo_angle(servos[i], latest_angles[i])
            last_update = now
