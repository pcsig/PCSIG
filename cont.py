# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 09:39:15 2022

@author: Cleber
"""
import os
a = 0

try:

    with open("descartada.txt", "r") as arquivo:
        cont = arquivo.read()
        lista = cont.split(',')
        print('Mensagens descartadas -> ', (len(lista)-1))         
                        
except:
    pass
    

with open("recebidas.txt", "r") as arquivo1:
    cont1 = arquivo1.read()
    lista1 = cont1.split(',')
    print('Mensagens recebidas -> ', len(lista1)-1)
    #print(lista1)       
    #print(f'valor total é {a}')


with open("progresso.txt", "r") as arquivo2:
    cont2 = arquivo2.read()
    lista2 = cont2.split(',')
    lista3 = [float(lista2[num]) for num in range(0, len(lista2)-1)]
    lista4 = [x for x in range(0, len(lista2)-1) if x != 0]
    print('Maior valor de progresso -> ', max(lista3))
    

try:
    #pass
    os.remove("recebidas.txt") 
    os.remove("progresso.txt")
    os.remove("descartada.txt")
except:
    pass
                

