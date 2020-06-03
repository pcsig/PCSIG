#!/usr/bin/python2.7
# coding: utf-8

import ast
unidirecional = 0
bidirecional = 0

def not_unique(el):
    global bidirecional
    if el:
        bidirecional += 1
        print(f'Bidirecional -> {bidirecional}')
arq = open('/home/cleber/Defesa/visaoSincronizada.txt', 'r')
texto = arq.readlines()[-1]

tlv_list = list(ast.literal_eval(texto))
[not_unique(i) if {'tempo': i['tempo'], 'lider': i['visao'], 'visao': i['lider']} in tlv_list else print('') for i in tlv_list]

cont = 0
for i in tlv_list:
    cont+=1
print(cont)
    
    
    



