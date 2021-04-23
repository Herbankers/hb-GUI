import sys, time, threading, serial, serial.tools.list_ports

class serialConnection:
    inputData = ""

    def __init__(self, port, baudrate):
        super(serialConnection, self).__init__()
        self.port = serial.Serial(port, baudrate, timeout=.1)
        print("connected to: " + self.port.portstr)
        self.port.flushInput()

    def send_data(self):
        data = input("Please enter the data to be sent:")
        print(data.encode())
        self.port.write(data.encode())  # send data
        print("command send:" + data)

    def read_data(self):  # receive data
        while True:
            try:
                if self.port.in_waiting > 0:
                    # #[:-2] removes last 2 characters which in this case will be the newline
                    data = self.port.readline()[:-2]
                    # decode the data
                    decoded_data = str(data, "utf-8").strip()
                    self.inputData = decoded_data
                    print(self.inputData)
            except:
                print("Keyboard interrupt")
                break
