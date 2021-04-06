import msgpack
import socket
import time

host = '127.0.0.1'
port = 8420

class HBP:
    HBP_VERSION =           1
    HBP_MAGIC =             0x4B9A208E
    HBP_PORT =              8420
    HBP_HEADER_LENGTH =     8

    # Constants
    HBP_ERROR_MAX =         10
    HBP_LENGTH_MAX =        32768
    HBP_IBAN_MIN =          9
    HBP_IBAN_MAX =          34
    HBP_PIN_MIN =           4
    HBP_PIN_MAX =           12
    HBP_PINTRY_MAX =        3
    HBP_TIMEOUT =           (5 * 60)
    HBP_CID_MAX =           12

    # Types of requests
    HBP_REQ_LOGIN =         0
    HBP_REQ_LOGOUT =        1
    HBP_REQ_INFO =          2
    HBP_REQ_BALANCE =       3
    HBP_REQ_TRANSFER =      4

    # Types of replies
    HBP_REP_LOGIN =         128
    HBP_REP_TERMINATED =    129
    HBP_REP_INFO =          130
    HBP_REP_BALANCE =       131
    HBP_REP_TRANSFER =      132
    HBP_REP_ERROR =         133

    # Indicates whether the login failed or succeeded
    HBP_LOGIN_GRANTED =     0
    HBP_LOGIN_DENIED =      1
    HBP_LOGIN_BLOCKED =     2

    # Indicates why the session has ended/the server will disconnect
    HBP_TERM_LOGOUT =       0
    HBP_TERM_EXPIRED =      1
    HBP_TERM_CLOSED =       2

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect((host, port))

    def send(self, request_type, data):
        packed = msgpack.packb(data, use_bin_type=True)

        header = bytearray()

        # magic
        # TODO get with masks, too lazy r.n.
        header.append(0x8E)
        header.append(0x20)
        header.append(0x9A)
        header.append(0x4B)

        # version
        header.append(self.HBP_VERSION)

        # type
        header.append(request_type)

        # length
        header.append((len(packed) & 0xFF))
        header.append(((len(packed) >> 8) & 0xFF))

        # send our request
        self.sock.sendall(header)
        self.sock.sendall(packed)

    def receive(self):
        # wait for the header to arrive
        header = self.sock.recv(self.HBP_HEADER_LENGTH)

        # check if the magic number is correct
        if header[0] != 0x8E or header[1] != 0x20 or header[2] != 0x9A or header[3] != 0x4B:
            print('received invalid HBP magic')
            exit(1)

        # check if we're using a compatible HBP version
        if header[4] != self.HBP_VERSION:
            print('received invalid HBP version')
            exit(1)

        # read the other fields into memory
        reply_type = header[5]
        length = header[6] | header[7] << 8

        # receive the msgpack data
        data = self.sock.recv(length)

        if reply_type == self.HBP_REP_ERROR:
            return (reply_type, 0)
        else:
            return (reply_type, {msgpack.unpackb(data, raw=False)})

    def request(self, request_type, data):
        self.send(request_type, data)
        return self.receive()

print('Copyright (C) 2021 Herbank CLI v1.0')
hbp = HBP(host, port)
print(f'Connected to Herbank Server @ {host}:{port}')
print('')

while True:
    card_id = input('Card ID: ')
    try:
        int(card_id)
    except ValueError:
        print("Invalid Card ID")
        continue

    pin = input('PIN: ')
    try:
        int(pin)
    except ValueError:
        print("Invalid PIN")
        continue

    data = [card_id, pin]
    print(hbp.request(hbp.HBP_REQ_LOGIN, data))
