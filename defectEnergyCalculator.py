# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 17:32:06 2024

@author: evanp
"""

import matplotlib.pyplot as plt
import pandas as pd
import os

#Folder Name of Save Location
saveFolderName = "chargeDefectsSeperated"

#Creates Folder if it does not exist
if not os.path.exists(saveFolderName):
    os.mkdir(saveFolderName)

testFile = pd.read_csv(r"./testFile.csv")

#Energy per Atom of Elements
elementNames = ["Rb", "Sb", "I"]
elementEPA = [-3.475, -4.061, -3.576]

E_f = 0.966852 #Fermi Energy (eV)
gap = 1.98 #Band Gap (eV)
stepSize = 0.01 #Size of Fermi Energy Step (eV)
iterations = gap/stepSize

bulkEnergy = float(testFile.iloc[0,2])

graphValues = []
fermiEnergies = []

#Plot Settings
ylimmax = 7
ylimmin = -9
xlimmax = gap
xlimmin = 0

#Generates all Fermi Energies for Plot
for i in range(0, int(iterations)):
    fermiEnergies.append(stepSize*i)
   
#Needed for Plots
storedName = testFile.iloc[1,0]

for i in range (1, len(testFile)):
    bulkDefectEnergy = float(testFile.iloc[i,2])
    # print(bulkDefectEnergy)
    
    defectName = testFile.iloc[i,0]
    
    j = 0
    firstElement = ""
    secondElement = ""
    
    while(defectName[j] != "_"):
        firstElement = firstElement + defectName[j]
        j = j + 1
        
    j = j + 1
    
    while(j != len(defectName)):
        secondElement = secondElement + defectName[j]
        j = j + 1
    
    finalDefectEnergy = bulkDefectEnergy - bulkEnergy 
    
    for k in range(0, len(elementNames)):
        #Subtract Energy From "Added" Element
        if(firstElement == elementNames[k]):
            finalDefectEnergy = finalDefectEnergy - elementEPA[k]
        
        #Add Energy From "Subtracted" Element
        if(secondElement == elementNames[k]):
            finalDefectEnergy = finalDefectEnergy + elementEPA[k]
    
    q = int(testFile.iloc[i, 1])
    V = float(testFile.iloc[i, 4])
    correction = float(testFile.iloc[i, 3])
    
    #Account for Charge Defect and Correction Values
    finalDefectEnergy = finalDefectEnergy + q*(E_f + V) + correction
    energy = '{:<12}  {:>6}'.format(defectName + "_" + str(q), str(round(finalDefectEnergy,5)))
    print(energy)
    
    
    #Everything Below is for plotting defect energy vs fermi energy
    for k in range(0, int(iterations)):
        graphValues.append(finalDefectEnergy + q*stepSize*k) #Adds the total fermi energy multiplied by charge
 
    if(storedName != defectName):
         plt.legend()
         saveLocation = saveFolderName + "/" + str(storedName) + ".png"
         plt.savefig(saveLocation)
         plt.show()
         storedName = defectName   
 
    plt.title("Defect Plot of " + defectName)
    plt.xlabel("Fermi Energy (eV)")
    plt.ylabel("Defect Energy (eV)")
    plt.plot(fermiEnergies, graphValues, label = str(q))
    plt.xlim(xlimmin, xlimmax)
    plt.ylim(ylimmin, ylimmax) 
    
    #Clear Graph Values
    graphValues = []
        
plt.legend()
saveLocation = saveFolderName + "/" + str(storedName) + ".png"
plt.savefig(saveLocation)
plt.show()           
    
    
