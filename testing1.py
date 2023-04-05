import node
import simpy
from datetime import datetime, timedelta

env = simpy.Environment()

# Construção da rede
# source ---> no1 \
#                  ----> no3
# source ---> no2 /
no1 = node.Node(env,4,1)
no2 = node.Node(env,6,2)
no3 = node.Node(env,10,1,3)

no1.nodeTargets.append(no3)
no2.nodeTargets.append(no3)

source = node.Source(env, [no1, no2])

# Processo
env.process(source.operate())
for node in [no1, no2, no3]:
    env.process(node.operate())

env.run(until=300)

#escrever os resultados no arquivo
with open("2023-03-27/event_log_s.txt","w") as event_log:
    event_log.write("case_id,activity_id,time_stamp,product_id")

with open("2023-03-27/event_log_s.txt","a") as event_log:
    timeST = datetime(2023, 9, 24, 9, 30, 35)
    for node in [no1, no2, no3]:
        for token, time in node.events:
            event_log.write(f"\n{token},{node.activityId},{timeST + timedelta(seconds=time)},{token}")


