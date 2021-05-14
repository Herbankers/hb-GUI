import getopt
import getpass
import os
import sys
import time

from hbp import *

hbp = None
arduino = None

def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def donate():
    choice = ''

    clear()
    print('')
    print(f'-[ Hoeveel geld wilt u doneren aan Bill Gates? ]-')
    print('')
    print('Help Bill Gates met de ontwikkeling van het corona virus.')
    print('')
    print('[1] EUR 2')
    print('[2] EUR 5')
    print('[3] EUR 10')
    print('[4] Handmatige invoer')
    print('[5] Afbreken')

    if arduino == None:
        choice = input('> ')
        try:
            int(choice)
        except ValueError:
            return True
    else:
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'K':
                choice = decoded_data[1:]
                break

    if choice == '1':
        amount = 2
    elif choice == '2':
        amount = 5
    elif choice == '3':
        amount = 10
    elif choice == '4':
        # TODO
        print('not yet implemented')
        sleep.time(5)
        return True
    elif choice == '5':
        return False
    else:
        return True

    reply = hbp.transfer('NL50BILL000000', amount * 100);

    if reply == hbp.HBP_TRANSFER_SUCCESS:
        clear()
        print('')
        print('Bedankt voor uw donatie!')
        time.sleep(3)
    elif reply == hbp.HBP_TRANSFER_PROCESSING:
        clear()
        print('')
        print('De transactie is nog in verwerking...')
        print('In ieder geval alvast bedankt voor uw donatie!')
        time.sleep(3)
    elif reply == hbp.HBP_TRANSFER_INSUFFICIENT_FUNDS:
        clear()
        print('')
        print('Uw saldo is ontoereikend')
        time.sleep(2)
    else:
        print(reply)
        time.sleep(2)

def withdraw():
    choice = ''

    clear()
    print('')
    print(f'-[ Hoeveel geld wilt u opnemen? ]-')
    print('')
    print('[1] EUR 10')
    print('[2] EUR 20')
    print('[3] EUR 50')
    print('[4] Handmatige invoer')
    print('[5] Afbreken')

    if arduino == None:
        choice = input('> ')
        try:
            int(choice)
        except ValueError:
            return True
    else:
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'K':
                choice = decoded_data[1:]
                break

    if choice == '1':
        amount = 10
    elif choice == '2':
        amount = 20
    elif choice == '3':
        amount = 50
    elif choice == '4':
        # TODO
        print('not yet implemented')
        sleep.time(5)
        return True
    elif choice == '5':
        return False
    else:
        return True

    reply = hbp.transfer('', amount * 100);

    if reply == hbp.HBP_TRANSFER_SUCCESS:
        clear()
        print('')
        print('Neem uw geld uit')
        time.sleep(3)
    elif reply == hbp.HBP_TRANSFER_PROCESSING:
        clear()
        print('')
        print('Neem uw geld uit (nog aan het verwerken)')
        time.sleep(3)
    elif reply == hbp.HBP_TRANSFER_INSUFFICIENT_FUNDS:
        clear()
        print('')
        print('Uw saldo is ontoereikend')
        time.sleep(2)
    else:
        print(reply)
        time.sleep(2)

def logout():
    # we can check the reply, but this is really not needed, as it basically always succeeds
    hbp.logout()

    clear()
    print('')
    print(f'Graag tot ziens!')

    time.sleep(3)

def mainmenu():
    choice = ''

    clear()
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
            return True
    else:
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'K':
                choice = decoded_data[1:]
                break

    if choice == '1':
        # Geld opnemen
        while withdraw():
            pass

        logout()
        return False
    elif choice == '2':
        # Geld doneren
        while donate():
            pass

        logout()
        return False
    elif choice == '3':
        # Saldo raadplegen
        clear()
        print('')
        print(f'Uw saldo is: EUR {hbp.balance()}')

        print('')
        print('Druk op een toets om terug te keren naar het hoofdmenu')

        if arduino == None:
            choice = input('')
        else:
            while True:
                data = arduino.readline()[:-2]
                decoded_data = str(data, 'utf-8')

                if decoded_data[0:1] == 'K':
                    break
    elif choice == '4':
        logout()
        return False

    return True

def login():
    card_id = ''
    iban = ''
    pin = ''

    clear()
    print('')

    if arduino == None:
        card_id = 'EBA8001B'
        iban = 'NL35HERB2932749274'

        pin = getpass.getpass('PIN: ')
        if pin == '':
            hbp.sock.close()
            exit(0)
        try:
            int(pin)
        except ValueError:
            clear()
            print('')
            print('Onjuiste PIN')
            time.sleep(3)
            return
    else:
        # Get the card ID from the card reader
        print('Houdt uw bankpas voor lezer om te beginnen')
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'U':
                card_id = decoded_data[1:]
                break
        #print(f'Kaart ID: {card_id}')

        # TODO should get this from the card too
        iban = 'NL35HERB2932749274'
        #print(f'IBAN: {iban}')

        clear()

        # Get the PIN input from the keypad
        print('')
        print('PIN: ', end='', flush=True)
        while True:
            data = arduino.readline()[:-2]
            decoded_data = str(data, 'utf-8')

            if decoded_data[0:1] == 'K':
                key = decoded_data[1:]
                pin += key
                #print(key, end='', flush=True)
                print('•', end='', flush=True)

                if len(pin) == 4:
                    break
        print('')

    reply = hbp.login(card_id, iban, pin)

    if reply == hbp.HBP_LOGIN_GRANTED:
        logged_in = True
        while logged_in:
            logged_in = mainmenu()
    elif reply == hbp.HBP_LOGIN_DENIED:
        clear()
        print('')
        print('Onjuiste PIN')
        time.sleep(2)
    elif reply == hbp.HBP_LOGIN_BLOCKED:
        clear()
        print('')
        print('Kaart geblokkeerd')
        time.sleep(2)
    else:
        print(reply)
        time.sleep(2)

# print usage information
def help():
    print('usage: cli.py [-h] [-s | --serial-port=] [-h | --host=] [-p | --port=]')

def main(argv):
    global hbp
    global arduino

    # parse command line options
    try:
        opts, args = getopt.getopt(argv, '?s:h:p:', [ 'serial-port=', 'host=', 'port=' ])
    except getopt.GetoptError:
        help()
        sys.exit(1)

    # empty input_souce means that we'll use the keyboard as input
    serial_port = ''

    host = '127.0.0.1'
    port = 8420

    for opt, arg in opts:
        if opt == '-?':
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

    if serial_port != '':
        arduino = serial.Serial(serial_port, 9600, timeout=.1)

    while True:
        login()

if __name__ == '__main__':
    main(sys.argv[1:])
