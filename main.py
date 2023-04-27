from flask import Flask, render_template, Response, request
import threading
import cv2
import RPi.GPIO as GPIO
import time
cv2.ocl.setUseOpenCL(False)

GPIO.setmode(GPIO.BOARD)


GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

def backward():
    GPIO.output(11, 0)
    GPIO.output(12, 1)

    GPIO.output(13, 0)
    GPIO.output(15, 1)


def forward():
    GPIO.output(11, 1)
    GPIO.output(12, 0)

    GPIO.output(13, 1)
    GPIO.output(15, 0)


def stop():
    GPIO.output(11, 1)
    GPIO.output(12, 1)

    GPIO.output(13, 1)
    GPIO.output(15, 1)



app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


def gen_frames():
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/gpio', methods=['POST'])
def gpio():
    value = request.form['value']
    if value == '0':
        forward()
    elif value == '1':
        backward()
    else:
        stop()
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
