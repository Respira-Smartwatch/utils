import matplotlib.pyplot as plt
import json

data = json.load(open('respira_Max_2023-02-22.json', 'r'))
phases = ['baseline', 'expiration1', 'rest1', 'expiration2', 'rest2', 'video', 'rest3', 'recitation', 'rest4']
phasic = []
tonic = []
print(data)
for i in phases:
	for j in data[i]['gsr_phasic']:
		phasic.append(j)
for i in phases:
	for j in data[i]['gsr_tonic']:
		tonic.append(j)
		
plt.plot(phasic)
plt.plot(tonic)
plt.title('GSR Test Data')
plt.ylabel('Skin Conductance Response')
plt.xlabel('Time')
plt.show()
