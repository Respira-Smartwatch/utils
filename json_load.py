import matplotlib.pyplot as plt
import json

data = json.load(open('joe.json', 'r'))
phases = ['baseline', 'expiration1', 'rest1', 'expiration2', 'rest2', 'video', 'rest3', 'recitation', 'rest4']
phasic = []
tonic = []


for i in phases:
	tonic.extend(data[i]["gsr_tonic"])	

print(tonic)
input()

plt.plot(tonic)
plt.title('GSR Test Data')
plt.ylabel('Skin Conductance Response')
plt.xlabel('Time')
plt.show()
