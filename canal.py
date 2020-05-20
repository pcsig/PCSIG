#!/usr/bin/python
# coding: utf-8

#Envio de mensagens

import socket
import time
import json
import numpy as np
import sys
import random

host = '255.255.255.255'
port = 44444

lider_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lider_socket.bind((host, port))

def enviarMensagem(mensagem, valor):
    timestamp = time.time()
    colisoes = []
    conjunto_colisoes = set()
    latencia = 0.02701
    t_aleatorio = random.uniform(0.001,0.030)

    ####################### Simulando perda e atraso de mensagens #####################

    resultado = np.arange (start = 1, stop = 3)
    perdaDeMensagens = np.random.choice (a = resultado, p = [1-valor, valor])
    time.sleep(latencia+t_aleatorio)
    if perdaDeMensagens == 1:
        message = json.dumps(mensagem)
        lider_socket.sendto(message.encode(), (host, port))
    else:
        message = json.dumps("lost")
        lider_socket.sendto(message.encode(), (host, port))

    ###########################  Contabilizando as colisões ###########################

    if message:
        with open('colisoes.txt', 'a') as arq:
            arq.write(str('{0:.6f}'.format(time.time())))
            arq.write(',')

    ##########################################################
