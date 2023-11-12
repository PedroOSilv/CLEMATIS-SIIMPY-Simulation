import pm4py
import node
import json
import simpy
from datetime import datetime, timedelta

#In this archive a petri net is converted to simulation model that uses the SimPy library

#create the SimPy Environment
env = simpy.Environment()

#read the petri net by using the pm4py library
pn = pm4py.read_pnml("generatedPetriNet.pnml")

#print the petriNet
pm4py.save_vis_petri_net(pn[0], pn[1], pn[2], 'petrinet.png')

#create a empty list of nodes
nodes = []

'''for i in pn[0].transitions:
    print(i.label)'''

#for each petri net place, we create a new node in this new model
for i in pn[0].places:
    newNode = node.Node(i.name,env)
    nodes.append(newNode)


#for each transition we create a edge on the new model
for i in nodes:
    for j in pn[0].transitions:

        #we take the list of arcs entering and going from the transition
        arcs_input  = list(j.in_arcs)
        arcs_output = list(j.out_arcs)
        
        #if we find a transition from the respective place, we link the ark into the node
        if i.activityId == str(arcs_input[0].source):
            
            #print("source arc ",arcs_input[0].source,"target",arcs_output[0].target)
            
            for k in nodes:
                if k.activityId == str(arcs_output[0].target):
                    i.nodeTargets.append(k)


#charge the JSON with the metadata 
f = open('graphInformation.json')
JSONnodeList = json.load(f)
metadataList = []

for i in JSONnodeList:
    jsonElement = json.loads(i)
    metadataList.append(jsonElement)

#charge the matadata into the node's object
initialTargetsList = []
for i in range(len(nodes)):
    jsonNode = metadataList[i]
    
    nodes[i].set_timeActivity(int(jsonNode["timeActivity"]))
    nodes[i].set_buffer(int(jsonNode["bufferSize"]))

    #find the nodes from the first production step
   
    if int(jsonNode["productionStep"]) == 0:
        for j in nodes:
            if int(jsonNode["activityId"]) == int(j.activityId):
                initialTargetsList.append(j)
    

#instantiating the inicial buffer with no limit of tokens
source =node.Source(env,initialTargetsList)

# bregin the simulation, first with the source node tha irrigates the first production step
env.process(source.operate())
for i in nodes:
    env.process(i.operate())

#simulate until reach a pre determined time in seconds
env.run(until=3000)

#write the results into a archive
with open("event_log.txt","w") as event_log:
    event_log.write("case_id,activity_id,time_stamp,product_id")

with open("event_log.txt","a") as event_log:
    timeST = datetime(2023, 9, 24, 9, 30, 35)
    for node in nodes:
        for token, time in node.events:
            event_log.write(f"\n{token},{node.activityId},{timeST + timedelta(seconds=time)},{token}")

print("Simulation was sucssesfuly made!")
