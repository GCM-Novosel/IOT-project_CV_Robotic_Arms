import board
import pwmio
import usb_cdc
import time
import digitalio

# LED setup
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Servo PWM outputs
pwm_pins = [board.GP7, board.GP8, board.GP9, board.GP10, board.GP11]
servos = [pwmio.PWMOut(pin, frequency=50) for pin in pwm_pins]

# Angle storage (latest parsed values)
latest_angles = [90] * 5  # Start centered
serial = usb_cdc.console
buffer = b""

# Convert angle (0-180) to PWM duty cycle
def set_servo_angle(pwm, angle):
    angle = max(0, min(180, angle))
    min_duty = 2 ** 16 * 0.030
    max_duty = 2 ** 16 * 0.120
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    pwm.duty_cycle = duty

# Boot blink
for _ in range(3):
    led.value = True
    time.sleep(0.2)
    led.value = False
    time.sleep(0.2)

# Main loop
last_update = time.monotonic()
while True:
    # Read latest serial data (non-blocking)
    while serial.in_waiting > 0:
        byte = serial.read(1)
        if byte == b'\n':
            try:
                line = buffer.decode("utf-8").strip()
                parts = line.split(",")
                if len(parts) == 5:
                    latest_angles = [max(0, min(180, int(p.strip()))) for p in parts]
                    led.value = True
                    time.sleep(0.01)
                    led.value = False
            except Exception:
                pass
            buffer = b""
        else:
            buffer += byte

    # Update servos every 50ms (20Hz)
    now = time.monotonic()
    if now - last_update >= 0.05:
        for i in range(5):
            set_servo_angle(servos[i], latest_angles[i])
        last_update = now
