
#!/usr/bin/python
# coding: utf-8

import simpy
import random
import queue
import numpy as np
import matplotlib.pyplot as plt
import copy

# Configuração do Random
SEED = 11
random.seed(SEED)
np.random.seed(SEED)

LATENCIA_CANAL = 25
PERDA_CANAL = 0
TEMPO_LIMITE = 1000

TEMPO_ENVIO = 500
T_ALEATORIO_MAX = 8
QUANTIDADE_LIDERES = 2
TEMPO_EXPERIMENTO = 103

environment = simpy.Environment()

##############################CANAL DE COMUNICAÇÃO ############################
class Canal(object):
    pacotesPerdidos = 0
    tamanhoFilaNoTempo = {'tamanho':[], 'tempo': []}
    mensangesNoTempo = {}

    def __init__(self, env):
        self.env = env
        self.q = queue.Queue()
        env.process(self.__run())

    def setLideres(self, lideres):
        self.lideres = lideres

    def difundir(self, mensagem):
        mensagem=copy.deepcopy(mensagem) #Tirar a referência (vários veículos usam o mesmo programa)
        if self.env.now not in self.mensangesNoTempo:
            self.mensangesNoTempo[self.env.now] = []
        self.mensangesNoTempo[self.env.now].append(mensagem)
        self.q.put(mensagem)

    def __encaminhar(self, messagem):
        for lider in lideres:
            lider.receber(messagem)

    def __getProximaMensagem(self):
        while True:
            if self.q.qsize():
                mensagem = self.q.get()
                resultado = np.arange (start = 1, stop = 3)
                perdaDeMensagens = np.random.choice (a = resultado, p = [1-PERDA_CANAL, PERDA_CANAL])
                if perdaDeMensagens == 1 and (self.env.now - mensagem[1][2]["tempo"]) <= TEMPO_LIMITE:
                    return mensagem
                else:
                    self.pacotesPerdidos += 1
                    print(f'PACOTES PERDIDO = {self.pacotesPerdidos}')
                    next
            else:
                return None

    def __run(self):
        while True:
            #print(f"[{self.env.now}] Tamanho Fila: {self.q.qsize()}")
            self.tamanhoFilaNoTempo['tamanho'].append([self.q.qsize()])
            self.tamanhoFilaNoTempo['tempo'].append([self.env.now])

            yield self.env.timeout(LATENCIA_CANAL)
            if self.q.qsize():
                self.__encaminhar(self.__getProximaMensagem())


################################## DENIFINIÇÃO DA CLASSE LÍDER ##################################               
class Lider(object):

    visoesSincronizadas = []
    visoesConhecidas = []
    visao = ()
    idVisao = 0    

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

################################### ETAPA DE MANUTENÇÃO DA TAREFA T2 ###################################
    def __manutencao(self):
        #mensagens Temporarias ← mensagensRecebidas
        mensagensTemporarias = list(self.mensagensRecebidas)
        visoesTemporarias = []            
        lideres = []
        
        mensagensTemporarias_aux = []
        if mensagensTemporarias != None:
            #para  cada m em mensagens Temporarias
            for m in mensagensTemporarias:
                #se m.idLider != idLider
                if m[0] != self.idLider:
                    if m[0] not in lideres:
                        lideres.append(m[0])
            for lider in lideres:
                for m in mensagensTemporarias:
                    if m[0] == lider:
                        vid_aux = m
                mensagensTemporarias_aux.append(vid_aux)
            #para  cada v em m.visoesConhecidas
            for vid in mensagensTemporarias_aux:
                vis = list(self.visao)
                v = vis[0:2]
                res = [v_id for v_id in vid[2]]
                for l2 in res:
                    vid2 = l2
                    #se v = visao
                    if v == vid2:
                        self.sincronizacoes.append({
                            'tempo': self.env.now,
                            'lider': self.idLider,
                            'visao': vid[0]
                        })
                        if self.env.now >= 2500:
                            with open('visaoSincronizada.txt', 'w') as arq_vis:
                                arq_vis.write(str(self.sincronizacoes))
                        #visoes Temporarias ← visoesTemporarias ∪ {m.visao}
                        visoesTemporarias.append(vid[0:-1])
            #visoesSincronizadas ← visoesTemporarias
            self.visoesSincronizadas = visoesTemporarias
            print(f"Visoes sincronizadas do lider: {self.idLider}, {self.visoesSincronizadas}")
            #visoesTemporarias ← ∅
            visoesTemporarias = []
            #mensagensRecebidas ← ∅
            self.mensagensRecebidas = []
        else:
            self.visoesSincronizadas = []
            print(f"Visoes sincronizadas do lider: {self.idLider}, {self.visoesSincronizadas}")
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
        tempAux = 0
        #enquanto True faça
        while True:
            yield self.env.timeout(1)
            #mensagensRecebidas ← mensagensRecebidas ∪ {receberM ensagem()}
            mensagem = self.__receberMensagem()
            if mensagem:
                delay = self.env.now - mensagem[1][2]["tempo"]
                if mensagem[0] not in self.delayMensagensNoTempo:
                    self.delayMensagensNoTempo[mensagem[0]] = {
                        'tempo': [],
                        'delay': []
                    }

                self.delayMensagensNoTempo[mensagem[0]]['delay'].append(delay)
                self.delayMensagensNoTempo[mensagem[0]]['tempo'].append(self.env.now)
                self.mensagensRecebidas.append(mensagem)
            #se cronometro = tempAux+tempoLimite
            if self.env.now == tempAux + TEMPO_LIMITE:
                #tempAux ← cronometro
                tempAux = self.env.now
                self.__manutencao()


################################## TAREFA T1 - ENVIO DE MENSAGENS ##################################
    def __enviar(self):
        #enquanto True faça
        while True:
            #sleep(periodo+tempoAleatorio)
            yield self.env.timeout(TEMPO_ENVIO + random.randint(0, T_ALEATORIO_MAX))
            v_id = self.idLider
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
            for lider in lideres:
                for m in self.mensagensRecebidas:
                    if m[0] == lider:
                        v_aux = m[1][0:2]
                #se m.idLider != idLider então
                if v_aux not in self.visoesConhecidas:
                    self.visoesConhecidas.append(v_aux)
            id = random.randint(0,1000000000)
            self.visao = v_id, self.idVisao, {'id_mensagem': id, 'tempo': self.env.now}
            #mensagem ← (idLider,visao,visoesConhecidas)
            mensagem = [self.idLider, list(self.visao), self.visoesConhecidas]
            #enviar Mensagem(mensagem)
            self.canalDeComunicacao.difundir(mensagem)

canal = Canal(environment)
lideres = []
for i in range(QUANTIDADE_LIDERES):
    lideres.append(Lider(environment, i, canal))
canal.setLideres(lideres)

############################### CRIÇÃO DE LOGS E GRÁFICOS ###############################

environment.run(TEMPO_EXPERIMENTO*1000)


colisoesNoTempo = [len(canal.mensangesNoTempo[key]) for key in canal.mensangesNoTempo.keys()]
#print(colisoesNoTempo)
#print(canal.mensangesNoTempo.keys())

fig, ax1 = plt.subplots()
ax1.set_xlabel('Tempo em segundos')
ax1.set_ylabel('Colisões')
ax1.plot(
    list(canal.mensangesNoTempo.keys()),
    colisoesNoTempo)
ax1.tick_params(axis='y', labelcolor='tab:red')
fig.tight_layout()
plt.show()

exit(0)

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

