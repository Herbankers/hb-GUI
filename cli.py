import time
import sys
import getopt
import getpass

from hbp import *

def mainmenu(hbp, arduino):
    choice = ''

    print('')

    # retrieve the name of the user
    name = hbp.info()
    if type(name) is list:
        print(f'-[ Welkom {name[0]} {name[1]} ]-')
    else:
        # name is not received for some strange reason
        print('Welcome!')

    print('')
    print('[1] Geld opnemen')
    print('[2] Geld doneren')
    print('[3] Saldo raadplegen')
    print('[4] Uitloggen')

    if arduino == None:
        choice = input('> ')
        try:
            int(choice)
        except ValueError:
            mainmenu(hbp, arduino)
    else:
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'K':
                choice = decoded_data[1:]
                break

    if choice == '1':
        print('Not Yet Implemented')
        mainmenu(hbp, arduino)
    elif choice == '2':
        print('Not Yet Implemented')
        mainmenu(hbp, arduino)
    elif choice == '3':
        print('Not Yet Implemented')
        mainmenu(hbp, arduino)
    elif choice == '4':
        # we can check the reply, but this is really not needed, as it basically always succeeds
        hbp.logout()
        print(f'Tot ziens {name[0]} {name[1]}!')

        login(hbp, arduino)
    else:
        print('Verkeerde keuze')
        mainmenu(hbp, arduino)

def login(hbp, arduino):
    card_id = ''
    iban = ''
    pin = ''

    print('')

    if arduino == None:
        card_id = '1223'
        iban = 'NL35HERB2932749274'

        pin = getpass.getpass('PIN: ')
        pin = input('PIN: ')
        try:
            int(pin)
        except ValueError:
            print('Foutieve PIN')
            login(hbp, arduino)
    else:
        # Get the card ID from the card reader
        print('Houd uw kaart voor de lezer')
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'U':
                card_id = decoded_data[1:]
                break
        print(f'Kaart ID: {card_id}')

        # TODO should get this from the card too
        iban = 'NL35HERB2932749274'
        print(f'IBAN: {iban}')

        # Get the PIN input from the keypad
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

    reply = hbp.login(card_id, iban, pin)

    if reply == hbp.HBP_LOGIN_GRANTED:
        mainmenu(hbp, arduino)
    elif reply == hbp.HBP_LOGIN_DENIED:
        print('Foutieve PIN')
        login(hbp, arduino)
    elif reply == hbp.HBP_LOGIN_BLOCKED:
        print('Kaart geblokkeerd')
        login(hbp, arduino)
    else:
        print(reply)
        login(hbp, arduino)

# print usage information
def help():
    print('usage: cli.py [-h] [-s | --serial-port=] [-h | --host=] [-p | --port=]')

def main(argv):
    # parse command line options
    try:
        opts, args = getopt.getopt(argv, 'hs:h:p:', [ 'serial-port=', 'host=', 'port=' ])
    except getopt.GetoptError:
        help()
        sys.exit(1)

    # empty input_souce means that we'll use the keyboard as input
    serial_port = ''

    host = '127.0.0.1'
    port = 8420

    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit(0)
        elif opt in ('-s', '--serial-port'):
            serial_port = arg
        elif opt in ('-h', '--host'):
            host = arg
        elif opt in ('-p', '--port'):
            port = arg

    print('Copyright (C) 2021 Herbank CLI v1.0')
    hbp = HBP(host, port)
    print(f'Connected to Herbank Server @ {host}:{port}')

    if serial_port == '':
        login(hbp, None)
    else:
        arduino = serial.Serial(serial_port, 9600, timeout=.1)
        login(hbp, arduino)

if __name__ == '__main__':
    main(sys.argv[1:])
