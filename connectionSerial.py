import serial, time
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

# arduino object with port, baud rate and timeout specified
arduino = serial.Serial(p[0], 9600, timeout=0.1)
print("connected to: " + arduino.portstr)
key = "/"


def retrieve_data():
    if arduino.in_waiting > 0:
        global key
        # #[:-2] removes last 2 characters which in this case will be the newline
        data = arduino.readline()[:-2]
        # decode the data
        key = str(data, "utf-8")
        print(key)


def send(data):
    arduino.write(data.encode())

while True:
    # print(key)
    if arduino.in_waiting > 0:
        retrieve_data()
    if key == "#":
        send("success")
    if key == "*":
        send("logout")
