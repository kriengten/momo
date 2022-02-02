import multiprocessing
import threading
import os
import time
import cv2
import sys
import datetime
import pathlib
from krieng import *

try:
    import mariadb
except:
    pass
import sqlite3
from sqlite3 import Error

def camera(source,path_to_save):
    record = 1
    next = 0
    path_record_array = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    cap = cv2.VideoCapture(source)
    while True:
        _,frame = cap.read()

        if frame is None:
            continue

        frame = cv2.resize(frame, (640, 360))
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


        cv2.rectangle(frame,(500,30),(610,50),(255,255,255),cv2.FILLED)
        cv2.putText(frame, '{}'.format(datetime.datetime.now().strftime("%T")), (500, 50), font, 0.8, (0, 0, 0), 1)
        a = str(source)
        if len(a) > 1:
            b = a.split(':')
            c = b[1].split('.')
            d = b[2].split('/')
            e = 'ip{}-port{}'.format(c[3],d[0])
        else:
            e = a
        file = e + '_' + "{}.mp4".format(Time_new)
        video_size = (640, 360)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # fourcc = cv2.VideoWriter_fourcc(*'H264')
        path_save_file = os.path.join(file_folder,file)

        if record == 1:
            rec = cv2.VideoWriter(path_save_file, fourcc, 50, video_size)
            record = 2

        if record == 2:
            rec.write(frame)
            if Time_new == '00-00-01':
                next = 0
            if Time_new == '00-00-00' and next == 0:
                record = 1
                next = 1
        cv2.imshow('frame: {}'.format(source),frame)
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
            os.mkdir(file_folder)
    except:
        print('Error to create file_folder')
        sys.exit(1)
    return path

def multiprocess_function(source,path_to_save):
    multi = multiprocessing.Process(target=camera, args=(source,path_to_save,))
    multi.start()
    # multi.join()

def threading_function(source,path_to_save):
    thread = threading.Thread(target=camera, args=(source,path_to_save,))
    thread.start()

def create_config(config_path,path_to_save,ip,port):
    write_config = ConfigParser()
    write_config.add_section('user')
    write_config.add_section('ip port store')
    write_config.add_section('note')

    write_config.set('user', 'path to save', path_to_save)
    write_config.set('user', 'mode', '1')
    write_config.set('user', 'number device for local', '1')

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
    no_user = 1
    read_config = ConfigParser()

    read_config.read(config_path)
    for each_section in read_config.sections():
        if each_section == 'user':
            path_to_save = read_config.get(each_section, 'path to save')
            mode = read_config.get(each_section, 'mode')
            number_d_local = read_config.get(each_section, 'number device for local')
            no_user = 0

        elif each_section == 'ip port store':
            for (each_key, each_val) in read_config.items(each_section):
                each_key = each_key[:2]
                if each_key == 'ip':
                    ip_array.append(each_val)
                else:
                    port_array.append(each_val)


    return path_to_save, mode,int(number_d_local) ,ip_array, port_array, no_user


if __name__ == '__main__':
    check_os = get_platform()
    if check_os == 'Windows':
        config_path = 'C:/Dropbox/config.ini'
    else:
        config_path = file_path
    while True:
        base_dir = pathlib.Path(__file__).parent.absolute()
        path_to_save, mode,number_d_local,ip_array, port_array, no_user = read_config(config_path)

        if no_user == 1:
            print('Add new user')
            print('\nDefault is base file directory')
            path_to_save = input('\nSelect path to save video: ')
            if path_to_save == '':
                path_to_save = str(base_dir)

            ip = input('\nIP: ')
            port = input('\nPort: ')

            create_config(config_path, path_to_save,ip,port)

        else:
            print('\nEnter to run')
            check_mode = input('>>> ')
            if check_mode == 'exit' or check_mode == 'q':
                break

            elif check_mode == 'test':
                for num_d in range(number_d_local):
                    source = num_d
                    if mode == '1':
                        multiprocess_function(source, path_to_save)
                    elif mode == '0':
                        threading_function(source, path_to_save)

            elif check_mode == 'run':
                for j in range(len(ip_array)):
                    source = 'http://{}:{}/videostream.cgi?user=admin&pwd=888888'.format(ip_array[j], port_array[j])
                    # source = 'http://{}:{}/video_feed'.format(ip_array[j], port_array[j])

                    if mode == '1':
                        multiprocess_function(source, path_to_save)
                    elif mode == '0':
                        threading_function(source, path_to_save)

            elif check_mode == '':
                pass

            else:
                print('invalid commard')