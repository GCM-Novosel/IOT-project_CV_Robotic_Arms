
import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt

# MQTT settings
UBIDOTS_TOKEN = "BBUS-0tCkaPMdIeHnTx63ArN7jDUhlxZ4yh"
UBIDOTS_BROKER = "industrial.api.ubidots.com"
UBIDOTS_PORT = 1883
DEVICE_LABEL = "OrangePi"

TOPIC_TEMPLATE = "/v1.6/devices/{}/{}"

# Fingers and their order for poses
FINGERS = ["index", "middle", "ring", "pinkie", "thumb"]

# Gesture to servo angle mapping [index, middle, ring, pinkie, thumb]
POSES = {
    "1":        [0, 180, 180, 180, 120],
    "2":        [0, 0, 180, 180, 120],
    "3":        [0, 0, 0, 180, 120],
    "4":        [0, 0, 0, 0, 120],
    "5":        [0, 0, 0, 0, 0],
    "peace":    [0, 0, 180, 180, 120],
    "rock_on":  [0, 180, 180, 0, 120],
    "ok":       [180, 180, 180, 180, 0],
    "fist":     [180, 180, 180, 180, 120],
    "open":     [0, 0, 0, 0, 0]
}

GESTURES = list(POSES.keys())

# MQTT Setup
client = mqtt.Client()
client.username_pw_set(UBIDOTS_TOKEN, password="")
client.connect(UBIDOTS_BROKER, UBIDOTS_PORT)
client.loop_start()

def publish(topic, value):
    payload = '{{"value": {}}}'.format(value)
    client.publish(topic, payload)
    print(f"Published to {topic}: {payload}")

class TouchUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robotic Hand Control")
        self.geometry("1027x600")
        self.attributes("-fullscreen", True)
        self.configure(bg="#1e1e1e")
        self.current_mode = "fingers"
        self.finger_states = {f: 0 for f in FINGERS}

        self.top_frame = tk.Frame(self, bg="#1e1e1e")
        self.top_frame.pack(pady=10)
        self.body_frame = tk.Frame(self, bg="#1e1e1e")
        self.body_frame.pack(expand=True)

        self.mode_button = tk.Button(self.top_frame, text="Switch to Gestures", command=self.toggle_mode, font=("Arial", 18), bg="#555", fg="white")
        self.mode_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(self.top_frame, text="Reset All", command=self.reset_all, font=("Arial", 18), bg="red", fg="white")
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(self.top_frame, text="Exit", command=self.quit, font=("Arial", 18), bg="#444", fg="white")
        self.exit_button.pack(side=tk.RIGHT, padx=10)

        self.bind("<Escape>", lambda e: self.destroy())
        self.render_finger_controls()

    def toggle_mode(self):
        if self.current_mode == "fingers":
            self.current_mode = "gestures"
            self.mode_button.config(text="Switch to Fingers")
            self.render_gesture_controls()
        else:
            self.current_mode = "fingers"
            self.mode_button.config(text="Switch to Gestures")
            self.render_finger_controls()

    def render_finger_controls(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        for i, finger in enumerate(FINGERS):
            btn = tk.Button(self.body_frame, text=finger.capitalize(), font=("Arial", 20), width=12, height=4,
                            bg="gray", fg="white", command=lambda f=finger: self.toggle_finger(f))
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)

    def render_gesture_controls(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        for i, gesture in enumerate(GESTURES):
            btn = tk.Button(self.body_frame, text=gesture, font=("Arial", 20), width=12, height=4,
                            bg="#444", fg="white", command=lambda g=gesture: self.send_gesture(g))
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)

    def toggle_finger(self, finger):
        self.finger_states[finger] ^= 1
        angle = 0 if self.finger_states[finger] else 180
        topic = TOPIC_TEMPLATE.format(DEVICE_LABEL, finger)
        publish(topic, angle)
        self.render_finger_controls()

    def reset_all(self):
        for f in FINGERS:
            self.finger_states[f] = 0
            topic = TOPIC_TEMPLATE.format(DEVICE_LABEL, f)
            publish(topic, 180)
        self.render_finger_controls()

    def send_gesture(self, gesture):
        if gesture in POSES:
            angles = POSES[gesture]
            for i, finger in enumerate(FINGERS):
                topic = TOPIC_TEMPLATE.format(DEVICE_LABEL, finger)
                publish(topic, angles[i])

if __name__ == "__main__":
    app = TouchUI()
    app.mainloop()
