from datetime import datetime, timedelta
import random
import simpy

#esse arquivo contem duas classes: Source e Node.
#   A classe source modela o gerador infinito de tokens
 
class Source:
    def __init__(self, env, nodeTargets):
        #env         -> Ambiente SimPy de simulação
        #nodeTargets -> Lista de nós alvos na primeira etapa de produção

        self.env = env
        self.nodeTargets = nodeTargets

    def operate(self):

        #contador de tokens para geração dos respectivos IDs
        token = 0

        while True:

            #para cada nó na primeira etapa de produção incremenete um token enquanto a simuação durar
            for node in self.nodeTargets:

                #yield self.env.timeout(1) # TODO deveria ter tempo zero de espera
                yield node.buffer.put(token) # XXX não deveria bloqueiar se o buffer do nó estiver cheio
                token = token + 1


# A Classe node modela cada nó do meu grafo
class Node:
    def __init__(self, *args):
        
        #env         -> Ambiente SimPy de simulação
        #buffer      -> Buffer de tokens do respectivo nó
        #activityId  -> Tempo de processamento de um token pelo nó
        #nodeTargets -> Lista de nós alvos, onde existe um arco direcionado, isto é a proxima maquina na linha de produção
        #events      -> Todos os eventos que aconteceram neste nó, que modela uma maquina em linha de produção.

        #tenho três condições para modelar três construtores diferentes, a depender do tipo de instanciação usada.
        #No caso de nós geradores de tokens utilizo um construtor onde não limito o tamanho do buffer
        if len(args) == 4:
            self.env = args[0]

            #declaro o tamanho do buffer deste nó com capacidade definida por parametro
            self.buffer = simpy.Store(self.env,capacity=args[1])
            self.timeActivity = args[2]
            self.activityId = args[3]
            self.nodeTargets = []
            self.events = []

        elif len(args) == 3:
            self.env = args[0]

            #declaro o tamanho do buffer deste nó com capacidade infinita
            self.buffer = simpy.Store(self.env)
            self.timeActivity = args[1]
            self.activityId = args[2]
            self.nodeTargets = []
            self.events = []

        elif len(args) == 2:
            self.env = args[1]

            #declaro o tamanho do buffer deste nó com capacidade infinita
            self.buffer = simpy.Store(self.env)
            self.timeActivity = 1
            self.activityId = args[0]
            self.nodeTargets = []
            self.events = []
        

    #este método simula a operação do respectivo nó
    def operate(self):
        while True:

            #retira um token do próprio buffer
            token = yield self.buffer.get()

            #espera o tempo de processamento deste respectivo nó
            yield self.env.timeout(self.timeActivity)

            #grava o id do token e o momento em que este foi processado neste nó
            self.events.append((token, self.env.now))

            #caso existam nós alvos, escolher um nó aleatório para realizar a passagem do token processado
            if len(self.nodeTargets) > 0:
                random.choice(self.nodeTargets).buffer.put(token)

    #setter do buffer, inicializa o buffer com um novo tamanho
    def set_buffer(self,bufferSize):
        if int(bufferSize) == 0:
            self.buffer = simpy.Store(self.env)
        else:
            self.buffer = simpy.Store(self.env,capacity=bufferSize)


    #setter do tempo da atividade
    def set_timeActivity(self,timeActivity):
        self.timeActivity = timeActivity
