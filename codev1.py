#!/usr/bin/env python3

import multiprocessing
import threading
import cv2
import sys
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
        try:
            connection = sqlite3.connect(database)
        except Error as e:
            print(f"Error connecting to sqlite Platform: {e}")
            sys.exit(1)

    cursor = connection.cursor()
    return cursor

def camera(source,st_thread=None):
    cap = cv2.VideoCapture(source)
    while True:
        _,frame = cap.read()

        cv2.imshow('frame: {}'.format(source),frame)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def multiprocess_function(source):
    multi = multiprocessing.Process(target=camera, args=(source,))
    multi.start()
    # multi.join()

def threading_function(source):
    thread = threading.Thread(target=camera, args=(source,))
    thread.start()

if __name__ == '__main__':
    ip_array = []
    port_array = []
    print('mode\n1:IP\n2:local')
    check_mode = input('select mode: ')
    print('\nrun mode\n1:Threading\n2:Multiprocessing')
    run_mode = input('select mode: ')
    print('\ndatabase\n1:mariadb\n2:sqlite')
    database_mode = input('select database: ')

    cursor = database(database_mode)

    count_device = input('\nHow many device: ')
    if check_mode == '1':
        for i in range(int(count_device)) :
            ip = input('IP: ')
            port = input('PORT: ')
            print('--- {}:{} ---'.format(ip,port))
            ip_array.append(ip)
            port_array.append(port)
    for j in range(int(count_device)):
        source = j
        if check_mode == '1':
            source = 'http://{}:{}/videostream.cgi?user=admin&pwd=888888'.format(ip_array[j], port_array[j])

        if run_mode == '1':
            print('Threading RUNNING')
            threading_function(source)
        elif run_mode == '2':
            print('Multiprocessing RUNNING')
            multiprocess_function(source)