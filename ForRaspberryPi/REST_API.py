import cv2
from flask import Flask, render_template
from flask import request
import serial
import time


ser = serial.Serial('COM4', 9600)  
time.sleep(2)
ser.reset_input_buffer()


app = Flask(__name__)


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
    elif command == 'off':
        ser.write(b'N')
    elif command == 'on':
        ser.write(b'O')  


@app.route("/")
def getPage():
	templateData = {
		'title' : 'Robot v1.0'
	}
	return render_template('index.html', **templateData)


@app.route('/qr_code')
def search_qr():
    code_key = request.args.get('code')
    if code_key is None:
        return 'Не передан код!', 400
    else:
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        while True:
            try:
                _, img = cap.read()
                data, vertices_array, _ = detector.detectAndDecode(img)
                if vertices_array is not None:
                    bb_pts = vertices_array.astype(int).reshape(-1, 2)
                    num_bb_pts = len(bb_pts)
                    for i in range(num_bb_pts):
                        cv2.line(img, tuple(bb_pts[i]), tuple(bb_pts[(i + 1) % num_bb_pts]), color=(0, 0, 255),
                                    thickness=2)
                        cv2.putText(img, data, (bb_pts[0][0], bb_pts[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0), 2)
                    if data:
                        if  data == code_key:
                            for i in range(num_bb_pts):
                                cv2.line(img, tuple(bb_pts[i]), tuple(bb_pts[(i + 1) % num_bb_pts]), color=(0, 255, 0),
                                            thickness=2)
                                cv2.putText(img, data, (bb_pts[0][0], bb_pts[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                            (0, 255, 0), 2)
                            print('Код верный')
                            break
                        else:
                            print('Код неверный')
                cv2.imshow('img', img)
                if cv2.waitKey(1) == ord('q'):
                    break
            except KeyboardInterrupt:
                print('Процесс был завершен')


@app.route("/forward", methods=['GET', 'POST'])
def forward():
	robot_movement('forward')
	return ('', 204)


@app.route("/backward", methods=['GET', 'POST'])
def backward():
	robot_movement('back')
	return ('', 204)

@app.route("/turnRight", methods=['GET', 'POST'])
def turn_right():
	robot_movement('right')
	return ('', 204)


@app.route("/turnLeft", methods=['GET', 'POST'])
def turn_left():
	robot_movement('left')
	return ('', 204)


@app.route("/stop", methods=['GET', 'POST'])
def stop():
	robot_movement('stop')
	return ('', 204)


@app.route("/offlight", methods=['GET', 'POST'])
def off():
	robot_movement('off')
	return ('', 204)


@app.route("/onlight", methods=['GET', 'POST'])
def on():
	robot_movement('on')
	return ('', 204)

if __name__ == '__main__':
    app.run()