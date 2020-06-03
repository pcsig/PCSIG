#!/usr/bin/python
# coding: utf-8

import socket
import time
import json
import threading
import numpy as np
import sys
import random

idLider = str(sys.argv[1])              #Define idLider
valor = float(sys.argv[2])              #Simulação de perda de mensagens
total_pelotoes = float(sys.argv[3])     #Quantidade de pelotões que deseja simular
tempoLimite = int(sys.argv[4])          #Valor do tempoLimite (1000; 2000; 3000; 4000; 5000 ms)
lista_mensagens = []
conjunto_colisoes = set()

v_id = idLider                              #é considerado que o id do líder endereça a visão
idVisao = 0                                 #o valor dessa variável é alterada sempre que há uma mudança de visão (no pseudocódigo, o idVisao e o v_id estão juntas
contexto = 'Platoon'                        #representa o contexto ou aplicação do grupo de veículos
periodo = 0.0                                 #variável utilizada para a contagem de tempo
atualizaVisao = 0                           #variável utilizada para auxiliar na simulação da atualização da visão
visao = ()                                  #tupla que recebe (v_id, idVisao, membros, contexto)
membros = ['l_1',  'f_1']                   #lista contendo os veículos que fazem parte do grupo. l_s líder e f1_s seguidor do grupo s
visoesSincronizadas = []                    #recebe as visões sincronizadas na TAREFA T3
mensagensRecebidas = []                     #recebe as mensagens na TAREFA T2
mensagensTemporarias = []                   #variável temporária utilizada na TAREFA T2
visoesTemporarias = []                      #variável temporária utilizada na TERAFE T3
visoesConhecidas = []
cronometro = 0                              #variável utilizada para a contagem de tempo
cont = 0.0
sinc = 0
i1 = 0
i2 = 0
cont_envia = 0
qtd = 0
envios = 0
sem = threading.Semaphore()
t_aleatorio = random.uniform(0.000000001,0.008)

host = '255.255.255.255'

lider_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
lider_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lider_socket.bind((host, 44444))

relogio_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
relogio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
relogio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
relogio_socket.bind((host, 44442))


#TAREFA T1: envio periódico de mensagens

def enviar():
    global mensagensRecebidas
    global idLider
    global idVisao, sem
    global atualizaVisao
    global visao
    global membros
    global visoesConhecidas
    global valor
    global cronometro
    lideres = []
    v_aux = []
    tempo = str('{0:.8f}'.format(cronometro))
    #linha 9 - para cada m em mensagensRecebidas faça:
    for m in mensagensRecebidas:
        #linha 10 - para cada v em visoesConhecidas faça:
        for v in visoesConhecidas:
            if v is None:
                print 'Visoes Conhecidas vazias'
            #linha 11 - se v.lider = m.idLider então:
            if m[0][0] == v[0][0]:
                #linha 12 - visoesConhecidas <- visoesConhecidas \ {v}
                visoesConhecidas.remove(v)
            else:
                pass
        #linha 15
        if m[0][0] != idLider:
            if m[0][0] not in lideres:
                lideres.append(m[0][0])
    for lider in lideres:
        for m in mensagensRecebidas:
            if m[0][0]==lider:
                v_aux = m[1][0:2]
        if v_aux not in visoesConhecidas:
            #linha 16 visoesConhecidas <- visoesConhecidas U {m.visao}
            visoesConhecidas.append(v_aux)
    sem.acquire()
    id = random.randint(0,1000000000)
    # tempo = str('{0:.8f}'.format(cronometro))
    visao = v_id, idVisao, [id,tempo], contexto
    #linha 19 mensagem <- (idLider,visao,visoesConhecidas)
    mensagem = idLider, list(visao), visoesConhecidas
    sem.release()
    #linha 20 enviarMensagem(mensagem)
    ############## marcação da latência (envio) ##############
    message = json.dumps(mensagem)
    lider_socket.sendto(message.encode(), (host, 44443))
    with open('marcTempo.csv', 'a') as arq:
        arq.write('E')
        arq.write(' ; ')
        arq.write(str(mensagem[0]))
        arq.write(' ; ')
        arq.write(tempo)
        arq.write(' ; ')
        arq.write(str(id))
        arq.write('\n')
    ##########################################################

def manutencao(*args):
    global mensagensTemporarias, sem
    global visoesSincronizadas
    global visoesTemporarias
    global visao
    global idLider
    global total_pelotoes
    global tempoLimite
    global cronometro
    global qtd
    mensagensTemporarias = list(args)
    lideres = []
    vid2 = []
    mensagensTemporarias_aux = []
    #linha 31 - para cada m em mensagensTemporarias:
    for m in mensagensTemporarias:
        #linha 32 - se m.idLider != idLider:
        if m[0][0] != idLider:
            if m[0][0] not in lideres:
                lideres.append(m[0][0])
    for lider in lideres:
        for m in mensagensTemporarias:
            if m[0][0] == lider:
                vid_aux = m
        mensagensTemporarias_aux.append(vid_aux)
    #linha 33 - para cada v em em visoesConhecidas faça:
    for vid in mensagensTemporarias_aux:
        vis = list(visao)
        v =  vis[0:2]
        res = [str(v_id) for v_id in vid[2]]
        for l2 in res:#linha 10 - para cada v em visoesConhecidas fala:
            vid2 = (l2[2:-1])
            #linha 34 - v = visao
            if str(v)[1:-1] == vid2:
                with open('visaoSincronizada.txt', 'a') as arq_vis:
                    arq_vis.write(str(round(cronometro,1)))
                    arq_vis.write(str(idLider))
                    arq_vis.write(vid[0])
                    arq_vis.write('\n')
                #linha 35 - visoesTemporarias <- visoesTemporarias U {v}
                visoesTemporarias.append(vid[0:-1])
    #linha 40 - visoesSincronizadas <- visoesTemporarias
    visoesSincronizadas = visoesTemporarias
    print 'Visoes sincronizadas do lider: ', idLider, visoesSincronizadas
    #linha 41 - visoesTemporarias <- 0
    del visoesTemporarias[:]
    #linha 42 - mensagensRecebidas <- 0
    del mensagensRecebidas[:]

#TAREFA T2: recebimento de mensagens
def receber():
    global mensagensRecebidas
    global cronometro
    global mensagensTemporarias
    global idLider
    global sem
    global tempoLimite
    global lista_mensagens
    #linha 25 - tempAux <- 0
    tempAux = 0.0
    t = tempoLimite/1000
    #linha 26 - enquanto True faça:
    while True:
        data, addr = lider_socket.recvfrom(4096)
        #tempo = str('{0:.8f}'.format(time.time()))
        receberMensagem2 = json.loads(data)
        #print receberMensagem2
        if receberMensagem2 != "lost":
            receberMensagem = receberMensagem2
            tempo = str('{0:.8f}'.format(cronometro))
            ############## marcação da latência (recebimento) ##############
            with open('marcTempo.csv', 'a') as arq:
                arq.write(' R ')
                arq.write(' ; ')
                arq.write(idLider)
                arq.write(' ; ')
                arq.write(str(receberMensagem[0]))
                arq.write(' ; ')
                arq.write(tempo)
                arq.write(' ; ')
                arq.write(str(receberMensagem[1][2]))
                arq.write(' ; ')
                arq.write(str(float(tempo)-float(receberMensagem[1][2][1])))
                arq.write('\n')
            ################################################################
        else:
            receberMensagem = [idLider, [idLider, 0, ["Platoon"], []]]
        #linha 27 - mensagensRecebidas <- mensagensRecebidas U {receberMensagem()}
        mensagensRecebidas.append(receberMensagem)
        #linha 28 - se cronometro = tempAux + tempoLimite entao
        gtgt = cronometro
        if int(gtgt) == int(tempAux) + t:
        #if round(cronometro,0) == tempAux + t:0
            sem.acquire()
            #linha 29 - mensagensTemporarias <- mensagensRecebidas
            mensagensTemporarias = mensagensRecebidas
            #linha 30 - tempAux <- cronometro
            tempAux = round(cronometro,1)
            t2_manutencao = threading.Thread(target=manutencao, args=mensagensTemporarias)
            t2_manutencao.start()
            sem.release()

tarefa2 = threading.Thread(target=receber)
tarefa2.start()

def manda():
    global cont_envia
    global valor
    tarefa1 = threading.Thread(target=enviar)
    tarefa1.start()
    cont_envia += 1

############################# CONTABILIZAÇÃO E VALIDAÇÃO DOS DADOS ##############################
    if cont_envia == 201:
        try:
            if tempoLimite == 1000:
                qtd = 100
                envios = 2
            elif tempoLimite == 2000:
                qtd = 50
                envios = 4
            elif tempoLimite == 3000:
                qtd = 33.33
                envios = 6
            elif tempoLimite == 4000:
                qtd= 25
                envios = 8
            elif tempoLimite == 5000:
                qtd = 20
                envios = 10
            else:
                print('Valor de tempo inválido')
            lista4 = []
            lista5 = []
            arq = open('/home/cleber/Defesa/visaoSincronizada.txt', 'r')
            texto = arq.readlines()
            arq.close()
            result = round(len(texto)/((total_pelotoes*(total_pelotoes-1))*(int(qtd))),4)
            print 'Sincronizações unidirecionais com o líder ', idLider, result*100, '%'
            lista1 = [str(float(lista)) for lista in range(1,101)]
            for l0 in lista1:
                lista2 = []
                for l1 in texto:
                    if l0[:3] == l1[:3]:
                        lista2.append(l1[-3:-1])
                lista3 = [i for i in lista2 if i[::-1] in lista2]
                num = len(lista3)
                lista4.append(num)
            soma = sum(lista4)
            result2 = round(soma/((total_pelotoes*(total_pelotoes-1))*(int(qtd))),4)
            print 'Sincronizações bidirecionais com o líder ', idLider, result2*100, '%'
            raw_input()
        except:
            print 'Não há visões sincronizadas!'
            raw_input()

############################## Relógio local ##############################

def relogioLocal(*args):
    global cronometro
    global t_aleatorio
    while True:
        data, addr = relogio_socket.recvfrom(4096)
        if data:
            start = json.loads(data)
            if start:
                cronometro+=0.5
                cronometro+=t_aleatorio
                manda()
tarefa4 = threading.Thread(target=relogioLocal)
tarefa4.start()

###########################################################################
