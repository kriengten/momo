#!/usr/bin/env python3

import multiprocessing
import os
import threading
import cv2
import sys
import datetime
import pathlib

try:
    import mariadb
except:
    pass
import sqlite3
from sqlite3 import Error

def database(database_mode):
    if database_mode == '1':
        host = input('host: ')
        if host == '':
            host = 'localhost'
        user = input('user: ')
        if user == '':
            user = 'root'
        passwd = input('password: ')
        database = input('database: ')
        try:
            connection = mariadb.connect(host=host, user=user, passwd=passwd, database=database)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
    elif database_mode == '2':
        database = input('database: ')
        if database == '':
            database = 'test.db'
        try:
            connection = sqlite3.connect(database)
        except Error as e:
            print(f"Error connecting to sqlite Platform: {e}")
            sys.exit(1)

    cursor = connection.cursor()


def camera(source,path_to_save,path_pre):
    record = 1
    next = 0
    path_record_array = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    cap = cv2.VideoCapture(source)
    while True:
        _,frame = cap.read()
        frame = cv2.resize(frame, (640, 360))
        Time = datetime.datetime.now().strftime("%T")
        Time_new = Time.replace(':', '-')
#        pathkri =pathlib.Path(__file__).parent.absolute()
        path = build_folder_file(path_to_save,path_pre)
        file_object = open('path_record.txt', 'r')
        lines = file_object.readlines()
        for file in lines:
            if file not in path_record_array:
                path_record_array.append(file)

        if path not in path_record_array:
            file_object = open('path_record.txt', 'a')
            file_object.write('\n{}'.format(path))
            file_object.close()


        cv2.rectangle(frame,(570,0),(625,13),(255,255,255),cv2.FILLED)
        cv2.putText(frame, '{}'.format(datetime.datetime.now().strftime("%T")), (570, 10), font, 0.4, (0, 0, 0), 1)

        file = str(source) + '_' + "{}.mp4".format(Time_new)
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

def build_folder_file(path_save,path_pre):
    global file_folder
#    base_dir = pathlib.Path(__file__).parent.absolute()
    base_dir = path_pre
#    projectroot = os.path.dirname(os.path.abspath(__file__))
#    base_dir = os.path.dirname(projectroot)
#    base_dir = os.path.dirname(os.path.abspath(__file__))
    # date_img = os.path.join(backup_img, "{}".format(datetime.date.today()))
    if path_save != '':
#        path = os.path.join(path_save,'record')
        base2 = str(path_pre)+"/"+str(path_save)+"/"
        path = os.path.join(base2,'record')
#        path = os.path.join(base_dir, 'record')
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

def threading_function(source,path_to_save,path_pre):
    thread = threading.Thread(target=camera, args=(source,path_to_save,path_pre,))
    thread.start()

# ------------------------------------------------------------------------------------------------------

def update_path_record():
    file_object = open('path_record.txt', 'r')
    lines = file_object.readlines()
    file_object.close()
    for line in lines[1:]:
        new_line = line.strip()
        isdir = os.path.isdir(new_line)
        if isdir == False:
            num_lines = lines.index(line)
            del lines[num_lines]
            new_file = open("path_record.txt", "w+")
            for line in lines:
                new_file.write(line)
            new_file.close()

def search_file():
    update_path_record()
    path_array = []
    num_array = []
    file_object = open('path_record.txt', 'r')
    lines = file_object.readlines()
    file_object.close()
    for count,line in enumerate(lines[1:]):
        line = line.strip()
        path_array.append(line)
        num_array.append(str(count))

    path_dict = dict(zip(num_array,path_array))
    print('\nPath to access')
    for n,p in path_dict.items():
        print('key: {} --> {}'.format(n,p))

    key = input('Choose key: ')

    record = path_dict[key]
    os.chdir(record)
    print('\nDate format: YYYY-MM-DD')
    date = input('Select Date: ')
    path_date = os.path.join(record,date)
    for file in os.listdir(path_date):
        file = os.path.join(date,file)
        video = cv2.VideoCapture(file)
        while True:
            _,frame = video.read()
            if frame is None:
                break
            cv2.putText(frame, "Press spacebar to play/pause", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 0), 2)
            cv2.imshow('frame',frame)
            k = cv2.waitKey(1)
            if k == ord('q'):
                break
            elif k == 32:
                cv2.waitKey(0)

if __name__ == '__main__':
    ip_array = []
    port_array = []
    # print('database\n1:mariadb\n2:sqlite')
    # database_mode = input('select database: ')
    # database(database_mode)
    print(pathlib.Path(__file__).parent.absolute())
    path_pre = pathlib.Path(__file__).parent.absolute()
    print('\nmode\n1:open camera\n2:search file')
    check_mode = input('select mode: ')

    if check_mode == '1':
        path_to_save = input('\nSelect path to save video: ')

        print('\nsource\n1:IP\n2:local')
        check_source = input('select source: ')
        print('\nrun mode\n1:Threading\n2:Multiprocessing')
        run_mode = input('select mode: ')

        count_device = input('\nHow many device: ')
        if check_source == '1':
            for i in range(int(count_device)) :
                ip = input('IP: ')
                port = input('PORT: ')
                print('--- {}:{} ---'.format(ip,port))
                ip_array.append(ip)
                port_array.append(port)
        for j in range(int(count_device)):
            source = j
            if check_source == '1':
                source = 'http://{}:{}/videostream.cgi?user=admin&pwd=888888'.format(ip_array[j], port_array[j])

            if run_mode == '1':
                print('Threading RUNNING')
                threading_function(source,path_to_save,path_pre)
            elif run_mode == '2':
                print('Multiprocessing RUNNING')
                multiprocess_function(source,path_to_save)
    elif check_mode == '2':
        search_file()