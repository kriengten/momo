import multiprocessing
import threading
import time
import cv2
import sys
import os
import numpy as np
import imutils

import datetime
import pathlib
from krieng import *

try:
    import mariadb
except:
    pass
import sqlite3
from sqlite3 import Error

count_array = []
store_frame0_array = [0]
store_frame1_array = [0]
store_frame2_array = [0]
store_frame3_array = [0]
store_frame4_array = [0]
store_frame5_array = [0]

def camera(source,path_to_save,skip_frame_ref):
    global store_frame0_array, store_frame1_array, store_frame2_array, store_frame3_array,store_frame4_array, store_frame5_array
    record = 1
    next = 0
    path_record_array = []
    skip_frame = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    # adjust resolution
    width = 320
    high = 180

    firstFrame = None
    cap = cv2.VideoCapture(source,cv2.CAP_DSHOW)

    while True:
        _,frame = cap.read()

        if frame is None:
            continue

        video_size = (width, high)
        frame = cv2.resize(frame, video_size)

        frame_motion = frame.copy()
        gray = cv2.cvtColor(frame_motion, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if firstFrame is None:
            firstFrame = gray
            continue
        frameDelta = cv2.absdiff(firstFrame, gray)
        firstFrame = gray
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        kernel = np.ones((8, 8), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=8)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        Time = datetime.datetime.now().strftime("%T")
        Time_new = Time.replace(':', '-')

        path = build_folder_file(path_to_save)
        file_object = open('path_record.txt', 'r')
        lines = file_object.readlines()
        for file in lines:
            if file not in path_record_array:
                path_record_array.append(file)

        if path not in path_record_array:
            file_object = open('path_record.txt', 'a')
            file_object.write('\n{}'.format(path))
            file_object.close()


        cv2.rectangle(frame,(width-100,10),(width-20,30),(255,255,255),cv2.FILLED)
        cv2.putText(frame, '{}'.format(datetime.datetime.now().strftime("%T")), (width-100, 30), font, 0.5, (0, 0, 0), 1)

        a = str(source)
        if len(a) > 1:
            b = a.split(':')
            c = b[1].split('.')
            d = b[2].split('/')
            e = 'ip{}-port{}'.format(c[3],d[0])

            # edit ip address position4
            if c[3] == '121':
                store_frame0_array.append(frame)
            elif c[3] == '121':
                store_frame1_array.append(frame)
            elif c[3] == '121':
                store_frame2_array.append(frame)
            elif c[3] == '121':
                store_frame3_array.append(frame)
            elif c[3] == '121':
                store_frame4_array.append(frame)
            elif c[3] == '121':
                store_frame5_array.append(frame)

            fps_video = 10
        else:
            e = a
            if e == '0':
                store_frame0_array[0] = frame
            elif e == '1':
                store_frame1_array[0] = frame
            elif e == '2':
                store_frame2_array[0] = frame
            elif e == '3':
                store_frame3_array[0] = frame
            elif e == '4':
                store_frame4_array[0] = frame
            elif e == '5':
                store_frame5_array[0] = frame

            fps_video =15

        file = e + '_' + "{}.mp4".format(Time_new)
        # video_size = (640, 360)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # fourcc = cv2.VideoWriter_fourcc(*'H264')
        path_save_file = os.path.join(file_folder,file)

        if record == 1:
            rec = cv2.VideoWriter(path_save_file, fourcc, fps_video, video_size)
            record = 2

        if record == 2:
            if cnts != []:
                rec.write(frame)
                record = 3
                if Time_new == '00-00-01':
                    next = 0
                if Time_new == '00-00-00' and next == 0:
                    record = 1
                    next = 1
        elif record == 3:
            skip_frame += 1
            if skip_frame == int(skip_frame_ref):
                record = 2
                skip_frame = 0
        cv2.imshow('frame: {}'.format(source),frame)
        # positionx = 0 + pox
        # positiony = 0 + poy
        # cv2.moveWindow('frame: {}'.format(source), positionx, positiony)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    cap.release()
    rec.release()
    cv2.destroyAllWindows()

def build_folder_file(path_save):
    global file_folder
    # date_img = os.path.join(backup_img, "{}".format(datetime.date.today()))
    if path_save != '':
        path = os.path.join(path_save,'record')
    else:
        path = os.path.join(base_dir, 'record')

    isfile = os.path.isfile('path_record.txt')
    if isfile == False:
        with open('path_record.txt', 'w') as f:
            f.write('list path')

    try:
        isdir = os.path.isdir(path)
        if isdir == False:
            os.mkdir(path)

    except Error as e:
        print(e)
        # print('Error to create path')
        sys.exit(1)

    file_folder = os.path.join(path, "{}".format(datetime.date.today()))
    try:
        isdir = os.path.isdir(file_folder)
        if isdir == False:
            os.makedirs(file_folder, exist_ok=True)
    except Error as e:
        print(e)
        # print('Error to create file_folder')
        sys.exit(1)
    return path

def multiprocess_function(source,path_to_save,skip_frame):
    multi = multiprocessing.Process(target=camera, args=(source,path_to_save,skip_frame,))
    multi.start()
    # multi.join()

def threading_function(source,path_to_save,skip_frame):
    thread = threading.Thread(target=camera, args=(source,path_to_save,skip_frame,))
    thread.daemon = True
    thread.start()

def create_config(config_path,path_to_save,ip,port):
    write_config = ConfigParser()
    write_config.add_section('user')
    write_config.add_section('ip port store')
    write_config.add_section('note')

    write_config.set('user', 'path to save', path_to_save)
    write_config.set('user', 'mode', '0')
    # write_config.set('user', 'number device for local', '1')
    write_config.set('user', 'choose source', '0 1 2 3')
    write_config.set('user', 'skip frame', '1')

    write_config.set('ip port store', 'ip1', ip)
    write_config.set('ip port store', 'port1', port)

    write_config.set('note', 'Threading', '0')
    write_config.set('note', 'Multiprocessing', '1')

    cfgfile = open(config_path, 'a')
    write_config.write(cfgfile)
    cfgfile.close()

def read_config(config_path):
    ip_array = []
    port_array = []
    path_to_save = ''
    mode = ''
    choose_source = ''
    skip_frame = ''
    no_user = 1
    read_config = ConfigParser()

    read_config.read(config_path)
    for each_section in read_config.sections():
        if each_section == 'user':
            path_to_save = read_config.get(each_section, 'path to save')
            mode = read_config.get(each_section, 'mode')
            # number_d_local = read_config.get(each_section, 'number device for local')
            choose_source = read_config.get(each_section, 'choose source')
            skip_frame = read_config.get(each_section, 'skip frame')
            # number_d_local = int(number_d_local)
            no_user = 0

        elif each_section == 'ip port store':
            for (each_key, each_val) in read_config.items(each_section):
                each_key = each_key[:2]
                if each_key == 'ip':
                    ip_array.append(each_val)
                else:
                    port_array.append(each_val)


    return path_to_save, mode,choose_source,skip_frame ,ip_array, port_array, no_user


check_os = get_platform()
if check_os == 'Windows':
    config_path = file_path_window
else:
    config_path = file_path_linux

base_dir = pathlib.Path(__file__).parent.absolute()