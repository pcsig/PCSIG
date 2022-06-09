#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 08:05:24 2021

@author: casa
"""

import simpy
import random
import queue
import numpy as np
import matplotlib.pyplot as plt
import copy

# Configuração do Random
seed: int = 100
random.seed(seed)
np.random.seed(seed)

latencia_canal: int = 1.86
perda_canal: float = 0
tempo_limite: int = 1000

tempo_envio: int = 100
t_aleatorio_max: int = 15
quantidade_lideres: int = 12
tempo_experimento: int = 21
lideres = []

environment = simpy.Environment()

##############################CANAL DE COMUNICAÇÃO##############################
class Canal(object):
    pacotesPerdidos:int = 0    
    tamanhoFilaNoTempo = {'tamanho':[], 'tempo': []}
    mensangesNoTempo = {}
    lideres=[]

    def __init__(self, env):
        self.env = env
        self.q = queue.Queue()
        env.process(self.__run())
        env.process(self.set_lideres(env))
    
    def remover_lider(self, idLider): 	
        for l in self.lideres:
            if l.idLider == idLider:
                self.lideres.remove(l)
    
    def adicionar_lider(self, idLider):
        lider = Lider(self.env, idLider, self)
        self.lideres.append(lider)
        lideres.append(lider)

    def set_lideres(self,env):
        yield self.env.timeout(0) 
        for i in range(quantidade_lideres):
            self.adicionar_lider(i)
        #yield self.env.timeout(50*1000) 
        #self.adicionar_lider(12)   #Comentar se quiser retirar o experimento de entrada de pelotão
        #yield self.env.timeout(20*1000)
        #self.remover_lider(0)

    def difundir(self, mensagem):
        mensagem=copy.deepcopy(mensagem) #Tirar a referência (vários veículos usam o mesmo programa)
        if self.env.now not in self.mensangesNoTempo:
            self.mensangesNoTempo[self.env.now] = []
        self.mensangesNoTempo[self.env.now].append(mensagem)
        self.q.put(mensagem)

    def __encaminhar(self, messagem):
        for lider in self.lideres:
            lider.receber(messagem)

    def __getProximaMensagem(self):
        while True:            
            if self.q.qsize():
                mensagem = self.q.get()
                resultado = np.arange (start = 1, stop = 3)
                perdaDeMensagens = np.random.choice (a = resultado, p = [1-perda_canal, perda_canal])
                print(f'tempo de progresso = {self.env.now - mensagem[1][2]["tempo"]}') # descomentar para tempo de progresso
                with open('progresso.txt', 'a') as arq_perd:
                    arq_perd.write(str(self.env.now - mensagem[1][2]["tempo"]))
                    arq_perd.write(str(","))
                if perdaDeMensagens == 1: 
                    if (self.env.now - mensagem[1][2]["tempo"]) > tempo_limite:
                        with open('descartada.txt', 'a') as descarte:
                            descarte.write(str(self.env.now - mensagem[1][2]["tempo"]))
                            descarte.write(str(','))                    
                    return mensagem
                else:
                    self.pacotesPerdidos += 1
                    print(f'PACOTES PERDIDO = {self.pacotesPerdidos}') #depois descomenta
                    with open('mensagenperdida.csv', 'a') as arq_perd:
                        arq_perd.write(str(self.pacotesPerdidos))
                        arq_perd.write(str(","))
                    next
            else:
                return None
    def __get_random(self,media,std):
        x = np.random.normal(media,std)
        return x if x > 0 else self.__get_random(media,std)
        
    def __run(self):
        while True:
            self.tamanhoFilaNoTempo['tamanho'].append([self.q.qsize()])
            self.tamanhoFilaNoTempo['tempo'].append([self.env.now])            
            #print(f'tamanho da fila {self.q.qsize()} t -> {self.env.now}')
            if self.q.qsize():
                mensagem = self.__getProximaMensagem()
                if mensagem != None:
                    #yield self.env.timeout(self.__get_range(latencia_canal,4))
                    yield self.env.timeout(latencia_canal + random.randint(1, t_aleatorio_max) + self.__get_random(0.5,0.2))
                    self.__encaminhar(mensagem)
                else:
                    yield self.env.timeout(1)
            else:
                yield self.env.timeout(1)


################################## DENIFINIÇÃO DA CLASSE LÍDER ##################################               
class Lider(object):
    mensagensRecebida:int = 0
    mensagenenviada:int = 0
    visoesSincronizadas = []
    visoesConhecidas = []
    visao = ()
    versao:int = 0    

    mensagensRecebidas = []
   
    sincronizacoes = []
    delayMensagensNoTempo = {}

    def __init__(self, env, idLider, canalDeComunicacao):
        self.q = queue.Queue()
        self.env = env
        self.idLider = idLider
        self.canalDeComunicacao = canalDeComunicacao
        env.process(self.__enviar())
        env.process(self.__receber())
        #env.process(self.__atualizaversao())    #Descomentar para simular variação do pelotão
        
    def __atualizaversao(self):
        #Experimento da dinamicidade dos multiplos pelotões
        yield self.env.timeout(((tempo_experimento*1000)/(quantidade_lideres+1))*(self.idLider+1))
        self.versao = self.versao+1
        print('versão do lider ', self.idLider, 'atualizada ', self.versao, ' ', self.env.now)      
        

################################### ETAPA DE MANUTENÇÃO DA TAREFA T2 ###################################
    def __manutencao(self,tempAux):
        #mensagens Temporarias ← mensagensRecebidas
        mensagensTemporarias = list(self.mensagensRecebidas)
        visoesTemporarias = []            
        lideres = []        
        mensagensTemporarias_aux = []
        if mensagensTemporarias != None:
            #para  cada m em mensagensTemporarias
            for m in mensagensTemporarias:
                #se m.cronometro≥(tempoLimite-tempAux)
                if m[-1] >= (self.env.now - tempAux):
                    #se m.idLider != idLider
                    if m[0] != self.idLider:
                        if m[0] not in lideres:
                            lideres.append(m[0])
            for l in lideres:
                for m in mensagensTemporarias:
                    if m[0] == l:
                        vid_aux = m
                mensagensTemporarias_aux.append(vid_aux)
            #para  cada v em m.visoesConhecidas
            #print(self.env.now, '=====', self.idLider) descomentar depois
            for vid in mensagensTemporarias_aux:
                vis = list(self.visao)
                v = vis[0:2]
                res = [v_id for v_id in vid[2]]
                for l2 in res:
                    vid2 = l2
                    #se v = visao  
                    #if (self.env.now - vid[1][2]["tempo"]) <= tempo_limite:
                    if v == vid2 and (self.env.now - vid[1][2]["tempo"]) <= tempo_limite:
                        self.sincronizacoes.append({
                            'tempo': self.env.now,
                            'lider': self.idLider,
                            'visao': vid[0]
                        })
                        with open('visaoSincronizada.txt', 'w') as arq_vis:
                            arq_vis.write(str(self.sincronizacoes))
                        #visoes Temporarias ← visoesTemporarias ∪ {m.visao}
                        visoesTemporarias.append(vid[0:-1])
            #visoesSincronizadas ← visoesTemporarias
            self.visoesSincronizadas = visoesTemporarias
            #print(f"Visoes sincronizadas do lider: {self.idLider}, {self.visoesSincronizadas}")
            #visoesTemporarias ← ∅
            visoesTemporarias = []
            #mensagensRecebidas ← ∅
            self.mensagensRecebidas = []
        else:
            self.visoesSincronizadas = []
            # print(f"Visoes sincronizadas do lider: {self.idLider}, {self.visoesSincronizadas}")
            #visoesTemporarias ← ∅
            visoesTemporarias = []
            #mensagensRecebidas ← ∅
            self.mensagensRecebidas = []
            pass

################################## TAREFA T2 - RECEBIMENTO DE MENSAGENS ##################################
            
    def receber(self, mensagem):
        self.q.put(mensagem)

    def __receberMensagem(self):
        if self.q.qsize():
            return self.q.get()
        else:
            return None

    def __receber(self):
        #tempAux←0
        tempAux:int = 0
        #enquanto True faça
        while True:
            yield self.env.timeout(1)
            #mensagensRecebidas ← mensagensRecebidas ∪ {receberM ensagem()}
            mensagem = self.__receberMensagem()            
            if mensagem:
                self.mensagensRecebida += 1
                if mensagem:
                    with open('recebidas.txt', 'a') as recebida:
                        recebida.write(str(self.env.now - mensagem[1][2]["tempo"]))
                        recebida.write(str(','))
                #print(f' Mensagens recebidas {self.mensagensRecebida}') #depois descomenta
                delay = self.env.now - mensagem[1][2]["tempo"]
                print(f'tempo de progresso = {delay}') # descomentar para tempo de progresso
                #print(f'Valor do delay -> {delay} -> {self.env.now}')
                #print(f'Mensagem -> {mensagem}')
                if mensagem[0] not in self.delayMensagensNoTempo:
                    self.delayMensagensNoTempo[mensagem[0]] = {
                        'tempo': [],
                        'delay': []
                    }
                self.delayMensagensNoTempo[mensagem[0]]['delay'].append(delay)
                self.delayMensagensNoTempo[mensagem[0]]['tempo'].append(self.env.now)
                self.mensagensRecebidas.append(mensagem)
            #se cronometro = tempAux+tempoLimite
            if self.env.now == tempAux + tempo_limite:
                #tempAux ← cronometro
                tempAux = self.env.now
                self.__manutencao(tempAux)


################################## TAREFA T1 - ENVIO DE MENSAGENS ##################################
    def __enviar(self):
        #enquanto True faça
        while True:
            #sleep(periodo+tempoAleatorio)
            yield self.env.timeout(tempo_envio) # + random.randint(0, t_aleatorio_max))
            lider = self.idLider
            lideres = []
            v_aux = []
            #para  cada m em mensagens Recebidas faça
            for m in self.mensagensRecebidas:
                #para  cada v em visoesConhecidas faça
                for v in self.visoesConhecidas:
                    if v is None:
                        pass
                    #se v.lider = m.idLider entao
                    if m[0] == v[0]:
                        self.visoesConhecidas.remove(v)
                    else:
                        pass                    
                if m[0] != self.idLider:
                    if m[0] not in lideres:
                        lideres.append(m[0])
            for l in lideres:
                for m in self.mensagensRecebidas:
                    if m[0] == l:
                        v_aux = m[1][0:2]
                #se m.idLider != idLider então
                if v_aux not in self.visoesConhecidas:
                    self.visoesConhecidas.append(v_aux)
            #id = random.randint(0,1000000000)
            #Composição da visão v=(lider, versao, membros) => a informação dos membros não é utilizado na simulação
            self.visao = lider, self.versao, {'tempo': self.env.now}
            #mensagem ← (idLider,visao,visoesConhecidas, cronometro)
            mensagem = [self.idLider, list(self.visao), self.visoesConhecidas, self.env.now]
            #enviar Mensagem(mensagem)
            self.canalDeComunicacao.difundir(mensagem)
            self.mensagenenviada += 1
            #print(f' Líder {lider} Enviou {self.mensagenenviada}')

canal = Canal(environment)

############################### CRIÇÃO DE LOGS E GRÁFICOS ###############################

environment.run(tempo_experimento*1000)

colisoesNoTempo = [len(canal.mensangesNoTempo[key]) for key in canal.mensangesNoTempo.keys()]
#print(colisoesNoTempo)
#print(canal.mensangesNoTempo.keys())

fig, ax1 = plt.subplots()
ax1.set_xlabel('Tempo em milissegundos')
ax1.set_ylabel('Colisões')
ax1.plot(
    list(canal.mensangesNoTempo.keys()),
    colisoesNoTempo)
ax1.tick_params(axis='y', labelcolor='tab:red')
fig.tight_layout()
plt.show()

#exit(0)

fig, ax1 = plt.subplots()
ax1.set_xlabel('Tempo')
ax1.set_ylabel('Tamanho da Fila', color='tab:red')
ax1.plot(
    canal.tamanhoFilaNoTempo['tempo'],
    canal.tamanhoFilaNoTempo['tamanho'],
    color='tab:red')
ax1.tick_params(axis='y', labelcolor='tab:red')

ax2 = ax1.twinx()
ax2.set_ylabel('Delay Msg De 1 para o 0', color='tab:blue')
ax2.plot(
    lideres[0].delayMensagensNoTempo[1]['tempo'],
    lideres[0].delayMensagensNoTempo[1]['delay'],
    color='tab:blue')

ax2.tick_params(axis='y', labelcolor='tab:blue')

# plt.plot( canal.tamanhoFilaNoTempo['tempo'],
#           canal.tamanhoFilaNoTempo['tamanho'])
fig.tight_layout()
plt.show()
