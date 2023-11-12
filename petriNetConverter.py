import argparse
import numpy as np
import json
import simpleNode
from igraph import *
from model_gen import ModelGeneratorNS
from pntools import petrinet as pn


# Para rodar basta inserir na linha de comando:
# python3 petriNetConverter.py -n <numero de nós> -s <numero de etapas de producao> -r <semente>

# take the parameters information from terminal
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--nodes", required=True, type=int)
ap.add_argument("-s", "--production_steps", required=True, type=int)
ap.add_argument("-f", "--first_step", type=int, default=-1)
ap.add_argument("-l", "--last_step", type=int, default=-1)
ap.add_argument("-r", "--seed", required=True, type=int) 
ap.add_argument("-t", "--production", default="constant")
ap.add_argument("-i", "--samples", type=int, default=30)

args = vars(ap.parse_args())

print("[INFO] Generating graph...")

#calls model gerenator
    #the returned parameters are: work_stations, production_edges, vertex_attr.
    #work_stations: the list of nodes
    #production_edges: the list of edges
    #vertex_attr: the node's properties
 
mg = ModelGeneratorNS(n=args["nodes"],
                      s=args["production_steps"],
                      first_step=args["first_step"],
                      last_step=args["last_step"],
					  buffer_size=3,
                      rng =np.random.default_rng( args["seed"]))

ws, edges, vertex_attr = mg.generate_graph()
# print(f"ws: {ws}")
# print(f"edges: {edges}")
# print(f"vertex_attr: {vertex_attr}")
                      
#create a petriNet object on pntools                      
net = pn.PetriNet()
net.name = "GeneratedPetriNet"

#printing the graph image
g = Graph(n=args["nodes"], edges=edges, directed=True,
				vertex_attrs=vertex_attr)

assert(g.is_dag())
plot(g, target='graph.png')

#create the places in the pntools object
for i in range(len(ws)):
    
    #lista de nos para etapa de producao
    step_node_list = ws[i]
    
    #para cada no na etapa de producao
    for j in range(len(step_node_list)):
        
        #crie um objeto do tipo place
        newPlace = pn.Place()
        
        #adicione uma legenda
        newPlace.label = str(step_node_list[j])
        
        #coloque o id do place para o id do nó
        newPlace.id = str(step_node_list[j])

        #adicione este lugar a petri net
        net.places[newPlace.id]=newPlace
    

#para cada aresta do grafo gerado
for i in edges:

    #crio duas arestas pois cada transicao tem no mínimo um aresta de entrada e outra de saida

    #crio e referencio a aresta1 criada a petriNet
    newEdge1 = pn.Edge()    
    newEdge1.net=net
    net.edges.append(newEdge1)

    #crio e referencio a aresta2 criada a petriNet
    newEdge2 = pn.Edge()
    newEdge2.net=net
    net.edges.append(newEdge2)

    #crio uma nova transicao
    newTransition = pn.Transition()
    source_label = " "
    target_label = " "

    #percorro os places da petriNet e encontro as arestas respectivas e as referencio
    for j in net.places:

        #se eu encontrar alguma aresta la lista de arestas do grafo, que pertence a este place eu referencio
        if net.places[j].label == str(i[0]):
            #marco a fonte desta aresta
            newEdge1.source = j
            #marco o alvo
            newEdge1.target = newTransition.id
            source_label = net.places[j].label

        if net.places[j].label == str(i[1]):
            #marco a fonte desta aresta
            newEdge2.source = newTransition.id
            #marco o alvo
            newEdge2.target = j
            target_label = net.places[j].label
            
        newTransition.label = source_label + " --> " + target_label
    
    #adiciono a transição na petriNet
    net.transitions[newTransition.id] = newTransition

#escrevo a petriNet em um arquivo
pn.write_pnml_file(net, "generatedPetriNet.pnml", relative_offset=True)

#if desired, insert the respective buffer size of each node
print("For each node inser the buffer size and time activity:")

#setting up the node's information
#  goes into all the steps
nodeList = []

for i in range(len(ws)):
    step_node_list = ws[i]
    print("production step:",i,"\n")
    #goes into all the nodes of each step
    a = input("Do you want to set a default value for the buffer size and time activity of this production step? y(yes) or n(no):")
    if a == 'y':
        bufferSize = int(input("Insert the default buffer size, insert 0 for infite buffer size: "))
        timeActivity = int(input("Insert the default time activity: "))
        for j in range(len(step_node_list)):
            print("Node:",step_node_list[j])
            productionStep = i

            #adding the metadata of the node in simple node class modelation
            newNode = simpleNode.simpleNode(timeActivity,step_node_list[j],bufferSize,productionStep)
            nodeList.append(newNode)
    else:
        for j in range(len(step_node_list)):
            print("Node:",step_node_list[j])
            bufferSize = int(input("Insert the buffer size: "))
            timeActivity = int(input("Insert the time activity: "))
            productionStep = i

            #adding the metadata of the node in simple node class modelation
            newNode = simpleNode.simpleNode(timeActivity,step_node_list[j],bufferSize,productionStep)
            nodeList.append(newNode)

#transform into a json file
JSONlist = []
for i in nodeList:
    JSONnode = json.dumps(i.__dict__)
    JSONlist.append(JSONnode)

#save the json into a file
with open('graphInformation.json', 'w') as json_file:
    json.dump(JSONlist, json_file)

print("The graph was sucessfuly generated!")


