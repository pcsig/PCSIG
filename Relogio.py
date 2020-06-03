#!/usr/bin/python
# coding: utf-8

import socket
import time
import json
import random
import threading

host = '255.255.255.255'

lider_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lider_socket.bind((host, 44441))

cont = 0

def relogioGlobal():
    time.sleep(2)
    global cont
    while True:
        time.sleep(0.5)
        cont += 1
        message = json.dumps(cont)
        lider_socket.sendto(message.encode(), (host, 44442))
tarefa4 = threading.Thread(target=relogioGlobal)
tarefa4.start()
