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
t_aleatorio = random.uniform(0.000000001,0.005)
contador =0.0

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
    for m in mensagensRecebidas:
        for v in visoesConhecidas:
            if v is None:
                print 'Visoes Conhecidas vazias'
                if m[0][0] == v[0][0]:
                    visoesConhecidas.remove(v)
                else:
                    print 'nok'
        if m[0][0] != idLider:
            if m[0][0] not in lideres:
                lideres.append(m[0][0])
    for lider in lideres:
        for m in mensagensRecebidas:
            if m[0][0]==lider:
                v_aux = m[1][0:2]
        if v_aux not in visoesConhecidas:
            visoesConhecidas.append(v_aux)
    sem.acquire()
    id = random.randint(0,1000000000)
    visao = v_id, idVisao, [id,tempo], contexto
    mensagem = idLider, list(visao), visoesConhecidas
    sem.release()
    ############## marcação da latência (envio) ##############
    time.sleep(t_aleatorio)
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
    if mensagensTemporarias != None:
        for m in mensagensTemporarias:
            if m[0][0] != idLider:
                if m[0][0] not in lideres:
                    lideres.append(m[0][0])
        for lider in lideres:
            for m in mensagensTemporarias:
                if m[0][0] == lider:
                    vid_aux = m
            mensagensTemporarias_aux.append(vid_aux)
        for vid in mensagensTemporarias_aux:
            vis = list(visao)
            v =  vis[0:2]
            res = [str(v_id) for v_id in vid[2]]
            for l2 in res:
                vid2 = (l2[2:-1])
                if str(v)[1:-1] == vid2:
                    with open('visaoSincronizada.txt', 'a') as arq_vis:
                        arq_vis.write(str(round(cronometro,1)))
                        arq_vis.write(str(idLider))
                        arq_vis.write(vid[0])
                        arq_vis.write('\n')
                    visoesTemporarias.append(vid[0:-1])
        visoesSincronizadas = visoesTemporarias
        print 'Visoes sincronizadas do lider: ', idLider, visoesSincronizadas
        del visoesTemporarias[:]
        del mensagensRecebidas[:]
    else:
        del visoesSincronizadas[:]
        print 'Visoes sincronizadas do lider: ', idLider, visoesSincronizadas
        del visoesTemporarias[:]
        del mensagensRecebidas[:]
        pass

#TAREFA T2: recebimento de mensagens
def receber():
    global mensagensRecebidas
    global cronometro
    global mensagensTemporarias
    global idLider
    global sem
    global tempoLimite
    global lista_mensagens
    tempAux = 0.0
    t = tempoLimite/1000
    ultimo = []
    while True:
        data, addr = lider_socket.recvfrom(4096)
        receberMensagem = json.loads(data)
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

        mensagensRecebidas.append(receberMensagem)
        if round(cronometro,1) == int(tempAux) + t:
            if mensagensRecebidas[:-1] != ultimo:
                ultimo = mensagensRecebidas[:-1]
                sem.acquire()
                mensagensTemporarias = mensagensRecebidas
                tempAux = round(cronometro,1)
                t2_manutencao = threading.Thread(target=manutencao, args=mensagensTemporarias)
                t2_manutencao.start()
                sem.release()
            else:
                sem.acquire()
                tempAux = round(cronometro,1)
                print 'no else perdeu mensagem ', tempAux
                t2_manutencao = threading.Thread(target=manutencao, args=mensagensTemporarias)
                t2_manutencao.start()
                pass
                sem.release()

tarefa2 = threading.Thread(target=receber)
tarefa2.start()

def mandar():
    global cont_envia
    global valor
    cont_envia += 1
    enviar()

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
            arq = open('/home/cleber/Defesa/visaoSincronizada.t    time.sleep(periodo)xt', 'r')
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
def esperar(esperar):
    tempoInicial = cronometro
    while True:
        tempoAtual, addr = relogio_socket.recvfrom(4096)
        cronometro=json.loads(tempoAtual)
        if cronometro - tempoInicial == espera:
            return

def relogioLocal(*args):
    global cronometro
    global contador
    global t_aleatorio
    while True:
        esperar(1)
        if data:
            mandar()
            esperar(5)
tarefa4 = threading.Thread(target=relogioLocal)
tarefa4.start()

###########################################################################
