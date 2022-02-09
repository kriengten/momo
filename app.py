import time
import socket

from flask import Flask, render_template, Response, request,jsonify
import cv2
import sys
from ipcam_v2 import *
app = Flask(__name__)


# camera = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    client_ip = request.remote_addr
    return client_ip

def get_frame(id):
    while True:
        out = store_frame0_array
        out2 = store_frame1_array
        out3 = store_frame2_array
        out4 = store_frame3_array
        out5 = store_frame4_array
        out6 = store_frame5_array

        if id == 0:
            ret, buffer = cv2.imencode('.jpg', out[0])
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elif id == 1:
            ret, buffer = cv2.imencode('.jpg', out2[0])
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elif id == 2:
            ret, buffer = cv2.imencode('.jpg', out3[0])
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elif id == 3:
            ret, buffer = cv2.imencode('.jpg', out4[0])
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elif id == 4:
            ret, buffer = cv2.imencode('.jpg', out5[0])
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        elif id == 5:
            ret, buffer = cv2.imencode('.jpg', out6[0])
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<string:id>/')
def video_feed(id):
    #Video streaming route. Put this in the src attribute of an img tag
    id = int(id)
    client_ip = get_my_ip()
    pox = 320 * id
    poy = 0
    if id > 2:
        id = id-3
        pox = 320 * id
        poy = 180
    return Response(get_frame(id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html',camera_list = count_array)

def app_run(host,port):

    app.run(host=host,port=port, threaded=True)

def run_server(host,port):
    record_thread = threading.Thread(target=app_run, args=(host,port,))
    record_thread.setDaemon(True)
    record_thread.start()

if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    port = 5000

    run_server(host,port)
    time.sleep(3)
    while True:
        path_to_save, mode,choose_source,skip_frame ,ip_array, port_array, no_user = read_config(config_path)
        if no_user == 1:
            print('Add new user')
            print('\nDefault is base file directory')
            path_to_save = input('\nSelect path to save video: ')
            if path_to_save == '':
                path_to_save = str(base_dir)

            ip = input('\nIP: ')
            port = input('\nPort: ')

            create_config(config_path, path_to_save, ip, port)

        else:
            print('\nEnter to run')
            check_mode = input('>>> ')
            if check_mode == 'q':
                break

            elif check_mode == 'test':
                cs = choose_source.split(' ')
                count_array = []
                for num_d in cs:
                    source = int(num_d)

                    if mode == '1':
                        multiprocess_function(source, path_to_save,skip_frame)
                    elif mode == '0':
                        threading_function(source, path_to_save,skip_frame)
                    count_array.append(source)

            elif check_mode == 'run':
                count_array = []
                for j in range(len(ip_array)):
                    source = 'http://{}:{}/videostream.cgi?user=admin&pwd=888888'.format(ip_array[j], port_array[j])
                    # rtsp://username:password@camera_ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp
                    # source = 'http://{}:{}/video_feed'.format(ip_array[j], port_array[j])

                    if mode == '1':
                        multiprocess_function(source, path_to_save,skip_frame)
                    elif mode == '0':
                        threading_function(source, path_to_save,skip_frame)
                    count_array.append(int(j))

            elif check_mode == '':
                pass

            else:
                print('invalid commard')