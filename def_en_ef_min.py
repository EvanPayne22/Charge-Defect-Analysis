# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 17:32:06 2024

@author: evanp
"""

import matplotlib.pyplot as plt
import pandas as pd
import os

#Folder Name of Save Location
saveFolderName = "chargeDefectPlots"

#Creates Folder if it does not exist
if not os.path.exists(saveFolderName):
    os.mkdir(saveFolderName)

testFile = pd.read_csv(r"./energies_final.csv")

#Energy per Atom of Elements
elementNames = ["Rb", "Sb", "I"]
elementEPA = [-3.475, -4.061, -3.576] #Condition 1  [-4.425, -6.911, -2.626] #Condition 4  [-4.518, -6.765, -2.628] #Condition 3 [-3.617, -4.061, -3.529] 
# Condtion 2   

E_f = 0.966852 #Fermi Energy (eV)
gap = 1.98 #Band Gap (eV)
stepSize = 0.01 #Size of Fermi Energy Step (eV)
iterations = gap/stepSize

bulkEnergy = float(testFile.iloc[0,2])

graphValues = []
fermiEnergies = []
#For graph of all defects on one plot
completeGraph = []
namesArray = []

#Plot Settings
ylimmax = 7
ylimmin = -9
xlimmax = gap
xlimmin = 0

count = 0

#Generates all Fermi Energies for Plot
for i in range(0, int(iterations)):
    fermiEnergies.append(stepSize*i)
   
#Gets the name of the first defect for plots
storedName = testFile.iloc[1,0]

for i in range (1, len(testFile)):
    bulkDefectEnergy = float(testFile.iloc[i,2])
    
    defectName = testFile.iloc[i,0]
    
    j = 0
    firstElement = ""
    secondElement = ""
    
    #Gets the name of the first element
    while(defectName[j] != "_"):
        firstElement = firstElement + defectName[j]
        j = j + 1
        
    j = j + 1
    
    #Gets the name of the second element
    while(j != len(defectName)):
        secondElement = secondElement + defectName[j]
        j = j + 1

    finalDefectEnergy = bulkDefectEnergy - bulkEnergy 
    
    #Calculates 
    for k in range(0, len(elementNames)):
        #Subtract Energy From "Added" Element
        if(firstElement == elementNames[k]):
            finalDefectEnergy = finalDefectEnergy - elementEPA[k]
            print(elementNames[k])
        
        #Add Energy From "Subtracted" Element
        if(secondElement == elementNames[k]):
            finalDefectEnergy = finalDefectEnergy + elementEPA[k]
            print(elementNames[k])
    q = int(testFile.iloc[i, 1])
    V = float(testFile.iloc[i, 4])
    correction = float(testFile.iloc[i, 3])
    
    #Account for Charge Defect and Correction Values
    finalDefectEnergy = finalDefectEnergy + q*(E_f + V) + correction
    energy = '{:<12}  {:>6}'.format(defectName + "_" + str(q), str(round(finalDefectEnergy,5)))
    print(energy)
    
    
    
 
    if(storedName != defectName and i != 1):
         tempArray = [] 
         forGraph = []
         
         #Appends minimum defetc energy at each fermi energy
         for m in range (0, int(len(graphValues)/count)):
             for n in range (0, count):
                 tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
             forGraph.append(min(tempArray))
             completeGraph.append(forGraph[m])
             tempArray = []
            
         #Plots the individual charge defect plots
         # plt.figure(figsize=(10,6))
         # plt.title("Defect Plot of " + storedName)
         # plt.xlabel("Fermi Energy (eV)")
         # plt.ylabel("Defect Energy (eV)")
         # plt.plot(fermiEnergies, forGraph)
         # plt.xlim(xlimmin, xlimmax)
         # plt.ylim(ylimmin, ylimmax)
         # saveLocation = saveFolderName + "/" + str(storedName) + ".png"
         # plt.savefig(saveLocation)
         # plt.show()
         
         namesArray.append(storedName)
         storedName = defectName
         
         #Clear Graph Values
         graphValues = []
         count = 0
    
    #Everything Below is for plotting defect energy vs fermi energy
    for k in range(0, int(iterations)):
        graphValues.append(finalDefectEnergy + q*stepSize*k) #Adds the total fermi energy multiplied by charge
    
    count = count + 1

#Erases temporary data for last graph
tempArray = [] 
forGraph = []

for m in range (0, int(len(graphValues)/count)):
    for n in range (0, count):
        tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
    forGraph.append(min(tempArray))
    completeGraph.append(forGraph[m])
    tempArray = []

#This plots the last individual defect
plt.figure(figsize=(10,6))
storedName = defectName
namesArray.append(storedName)
# plt.title("Defect Plot of " + defectName)
# plt.xlabel("Fermi Energy (eV)")
# plt.ylabel("Defect Energy (eV)")
# plt.plot(fermiEnergies, forGraph, label = str(q))
# plt.xlim(xlimmin, xlimmax)
# plt.ylim(ylimmin, ylimmax)
# saveLocation = saveFolderName + "/" + str(storedName) + ".png"
# plt.savefig(saveLocation)
# plt.show()

numberOfDefects = int(len(completeGraph)/len(fermiEnergies))


plt.figure(figsize=(3.5,6))
plt.title("Charge Defect Plot")
plt.xlabel("Fermi Energy (eV)")
plt.ylabel("Defect Energy (eV)")
plt.xlim(xlimmin, xlimmax)
plt.ylim(ylimmin, ylimmax)
for i in range(0, numberOfDefects):
    tempData = []
    for j in range(0, int(len(fermiEnergies))):
        tempData.append(completeGraph[i*len(fermiEnergies) + j])
    
    plt.plot(fermiEnergies, tempData, label = namesArray[i])
    

plt.legend()
saveLocation = saveFolderName + "/" + "combinedDefects.png"
plt.savefig(saveLocation)
plt.show()

        
    
         
    
    
