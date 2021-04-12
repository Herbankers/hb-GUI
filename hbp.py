import msgpack
import socket
import getpass
import time
import serial

host = '127.0.0.1'
port = 8420

arduino = serial.Serial('/dev/tty.usbmodem14201', 9600, timeout=.1)

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

    def replyType(self, reply_type):
        # TODO put in a list or something but i was lazy
        if reply_type == self.HBP_REP_LOGIN:
            return 'HBP_REP_LOGIN'
        elif reply_type == self.HBP_REP_TERMINATED:
            return 'HBP_REP_TERMINATED'
        elif reply_type == self.HBP_REP_INFO:
            return 'HBP_REP_INFO'
        elif reply_type == self.HBP_REP_BALANCE:
            return 'HBP_REP_BALANCE'
        elif reply_type == self.HBP_REP_TRANSFER:
            return 'HBP_REP_TRANSFER'
        elif reply_type == self.HBP_REP_ERROR:
            return 'HBP_REP_ERROR'

    def request(self, request_type, data):
        self.send(request_type, data)
        return self.receive()

def mainmenu():
    # TODO retrieve name via request
    name = 'G. Frey'

    print('')
    print(f'-[ Welkom {name} ]-')
    print('')
    print('[1] Geld opnemen')
    print('[2] Geld doneren')
    print('[3] Saldo raadplegen')
    print('[4] Uitloggen')

    choice = '-'
    while True:
        data = arduino.readline()[:-2]
        decoded_data = str(data, 'utf-8')

        if decoded_data[0:1] == 'K':
            choice = decoded_data[1:]
            break

    if choice == '1':
        print('Not Yet Implemented')
        mainmenu()
    elif choice == '2':
        print('Not Yet Implemented')
        mainmenu()
    elif choice == '3':
        print('Not Yet Implemented')
        mainmenu()
    elif choice == '4':
        logout_reply = hbp.request(hbp.HBP_REQ_LOGOUT, [])
        print(f'Tot ziens {name}!')
        # TODO we can check the reply, but this is really not needed, as it basically always succeeds
        login()
    else:
        print('Verkeerde keuze')
        mainmenu()

def login():
    print('')

    # Get the card ID from the card reader
    print('Houd uw kaart voor de lezer')
    card_id = ''
    while True:
        data = arduino.readline()[:-2]
        decoded_data = str(data, 'utf-8')

        if decoded_data[0:1] == 'U':
            card_id = decoded_data[1:]
            break
    print(f'Kaart ID: {card_id}')

    # TODO should get this from the card too
    account = 'NL35HERB2932749274'
    print(f'IBAN: {account}')

    # Get the PIN input from the keypad
    pin = ''
    print('PIN: ', end='', flush=True)
    while True:
        data = arduino.readline()[:-2]
        decoded_data = str(data, 'utf-8')

        if decoded_data[0:1] == 'K':
            key = decoded_data[1:]
            pin += key
            print(key, end='', flush=True)

            if len(pin) == 4:
                break
    print('')

    #pin = getpass.getpass('PIN: ')
    #pin = input('PIN: ')
    #try:
    #    int(pin)
    #except ValueError:
    #    print('Foutieve PIN')
    #    login()

    login_request = [card_id, account, pin]
    login_reply = hbp.request(hbp.HBP_REQ_LOGIN, login_request)

    reply_type = login_reply[0]
    if reply_type != hbp.HBP_REP_LOGIN:
        print(f'Received wrong reply: {hbp.replyType(reply_type)}')
        login()

    reply_status = list(login_reply[1])[0]
    if reply_status == hbp.HBP_LOGIN_GRANTED:
        mainmenu()
    elif reply_status == hbp.HBP_LOGIN_DENIED:
        print('Foutieve PIN')
        login()
    elif reply_status == hbp.HBP_LOGIN_BLOCKED:
        print('Kaart geblokkeerd')
        login()
    else:
        print('Erroneous login reply status')
        login()

print('Copyright (C) 2021 Herbank CLI v1.0')
hbp = HBP(host, port)
print(f'Connected to Herbank Server @ {host}:{port}')

login()
