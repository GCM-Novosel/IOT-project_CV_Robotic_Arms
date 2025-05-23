import serial
ser = serial.Serial("COM5", 115200)
ser.write(b"90,90,90,90,90\n")  # Should blink 1x
ser.write(b"90,90,90\n")        # Should blink 3x
ser.write(b"bad,data\n")        # Should blink 10x