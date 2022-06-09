# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 06:59:58 2022

@author: Cleber
"""

#!/usr/bin/python2.7
# coding: utf-8

import ast
unidirecional = 0
bidirecional = 0

arq = open(r'C:\Users\Cleber\.spyder-py3/visaoSincronizada.txt')
texto = arq.readlines()[-1]

def not_unique(el):
    global bidirecional
    if el:
        print(el)
        bidirecional += 1
        #print(f'Bidirecional -> {bidirecional}')


def unique(el):
    global unidirecional
    unidirecional += 1
    #print(f'Unidirecional -> {unidirecional}')

tlv_list = list(ast.literal_eval(texto))
[not_unique(i) if {'tempo': i['tempo'], 'lider': i['visao'], 'visao': i['lider']} in tlv_list else unique(i) for i in tlv_list]

    
print(f'Vizinhança estável -> {(bidirecional/2)}')
print(f'Vizinhança instável -> {unidirecional}' )
    


