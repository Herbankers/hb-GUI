import serial, time
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

# #arduino object with port, baud rate and timeout specified
arduino = serial.Serial(p[0],9600,timeout=.1)
print("connected to: " + arduino.portstr)

while(True):
    if(arduino.in_waiting > 0):
        # #[:-2] removes last 2 characters which in this case will be the newline
        data = arduino.readline()[:-2]
        #decode the data
        decoded_data = str(data,'utf-8')
        print(decoded_data)

