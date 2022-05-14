import cv2
from flask import Flask
from flask import request


app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7092)