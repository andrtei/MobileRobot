import serial
import time


ser = serial.Serial('/dev/cu.usbserial-120', 9600)  
time.sleep(2)
ser.reset_input_buffer()


def robot_movement(command):
    if command == 'forward':
        ser.write(b'F')
    elif command == 'stop':
        ser.write(b'S')
    elif command == 'right':
        ser.write(b'R')
    elif command == 'back':
        ser.write(b'B')
    elif command == 'left':
        ser.write(b'L')


def start_program():
    while True:
        time.sleep(1)
        command = input('Выберите команду - stop/forward/left/right: ')
        if command is not None:
            robot_movement(command)
            print(f'Команда - {command} ')
        else:
            continue


if __name__ == '__main__':
    print('Начинаю работу...')
    start_program()