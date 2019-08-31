#!/usr/bin/python
# coding: utf-8
import socket
import time
import json
import threading

l_id = 'r'
v_id = l_id
c = 'Platoon'
Buffer = []
TO = 10
timer = 0
timestamp = 0
aux_timestamp = 0
V_temp = []
V_sync = []
Buffer_recv = []
idp = 0

sem = threading.Semaphore()

host = '255.255.255.255'
port = 44444

leaderr_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
leaderr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
leaderr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

leaderr_socket.bind((host, port))

def enviar():
    global timestamp
    global timer
    #global V_Temp
    global Buffer
    global l_id
    global idp, sem
    lideres = []
    Lista_vid = []
    v_aux = []
    if timer == 5:
        for msg in Buffer:
            if msg[0][0] != l_id:
		if msg[0][0] not in lideres:
                    lideres.append(msg[0][0])
	#print 'Lideres T1 ', lideres
        for lider in lideres:
            for msg in Buffer:
                if msg[0][0] == lider:
                    v_aux = msg[1][0:2]
            Lista_vid.append(v_aux)
        M = ['l_r', 'f1_r']
        idp += 1
        v = (v_id, idp, M, c)
        timestamp += 5
        sem.acquire()
        m = l_id, list(v), Lista_vid, timestamp
        #print 'Lista enviada ', m
        sem.release()
        message = json.dumps(m)
        leaderr_socket.sendto(message.encode(), (host, port))
        timer = 0

def manutencao(*args):
    global V_temp, sem
    global V_sync
    sem.acquire()
    V_temp = []
    V_temp = list(args)
    lideres = []
    V_sync = []
    V_syncaux = []
    #print 'Valor recebido da tarefa 2 ', V_temp
    for msg in V_temp:
        if msg[0][0] != l_id:
            if msg[0][0] not in lideres:
                lideres.append(msg[0][0])
    #print 'Lista dos lideres ', lideres
    for lider in lideres:
        for msg in V_temp:
            if msg[0][0] == lider:
                vid_aux = msg
        V_syncaux.append(vid_aux)
	#print 'Lista recebida na t3 ', V_syncaux
    for msg in V_syncaux:
        for vid in msg[2]:
            if vid[0] == l_id:
                if vid[1] >= (idp-5):
                    V_sync.append(msg)
    print 'Visões sincronizadas ', V_sync
    sem.release()

def receber():
    global Buffer
    global timestamp
    global aux_timestamp
    #global V_temp
    global Buffer_recv
    while True:
        data, addr = leaderr_socket.recvfrom(4096)
        B2 = json.loads(data)
        if data:
            Buffer.append(B2)
            #print 'Lista do Buffer ', Buffer 
            if timestamp == aux_timestamp + TO:
                sem.acquire()
                aux_timestamp = timestamp
                Buffer_recv = Buffer
                Buffer = []
                tarefa3 = threading.Thread(target=manutencao, args=Buffer_recv)
                tarefa3.start()
                sem.release()

tarefa2 = threading.Thread(target=receber)
tarefa2.start()

while True:
    time.sleep(1)
    timer = timer + 1
    tarefa1 = threading.Thread(target=enviar)
    tarefa1.start()
