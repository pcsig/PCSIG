#!/usr/bin/python
# coding: utf-8

import socket
import time
import json
import numpy as np
import sys
import random
import queue
import threading

perda = float(sys.argv[1])              #Simulação de perda de mensagens

host = '255.255.255.255'

lider_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lider_socket.bind((host, 44443))

timestamp = time.time()
colisoes = []
conjunto_colisoes = set()
latencia = 0.025
l_msn = []
q = queue.Queue()
tam_fila = 0

def buffer():
    global perda
    global tam_fila
    while True:
        data, addr = lider_socket.recvfrom(4096)
        recb_canal = json.loads(data)
        if recb_canal:
            q.put(recb_canal)
            tam_fila = q.qsize()
            print tam_fila
        ######################### Fila #########################
        with open('fila.csv', 'a') as arq:
            arq.write(str(recb_canal[0]))
            arq.write(' ; ')
            arq.write(str(q.qsize()))
            arq.write('\n')
        ########################################################

def encaminhar():
    global tam_fila
    while True:
        if not q.empty():
            time.sleep(latencia)
            mensagem = q.get()
            resultado = np.arange (start = 1, stop = 3)
            perdaDeMensagens = np.random.choice (a = resultado, p = [1-perda, perda])
            if perdaDeMensagens == 1 and tam_fila < 20:
                message = json.dumps(mensagem)
                lider_socket.sendto(message.encode(), (host, 44444))
            else:
                message = json.dumps("lost")
                lider_socket.sendto(message.encode(), (host, 44444))
        else:
            time.sleep(0.0001)

tarefaBuffer = threading.Thread(target=buffer)
tarefaBuffer.start()

tarefaEncaminhar = threading.Thread(target=encaminhar)
tarefaEncaminhar.start()
