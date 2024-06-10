# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 13:15:19 2024

@author: evanp
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import yaml

# Folder Name of Save Location for charge defect plots
saveFolderNameCharge = "chargeDefectPlots"

# Folder Name of Save Location for charge defect plots
saveFolderNameVAtoms = "vAtomsImages"

# Creates Folder if it does not exist
if not os.path.exists(saveFolderNameCharge):
    os.mkdir(saveFolderNameCharge)
if not os.path.exists(saveFolderNameVAtoms):
    os.mkdir(saveFolderNameVAtoms)

#Insert all files below
#vAtoms Data
data = pd.read_csv(r".\vAtoms_output.csv").astype(str)
#Initial Energies Data
finalFile = pd.read_csv(r"./correctionEnergies.csv")
#Chem Potentials File
with open(r'.\target_vertices.yaml', 'r') as file:
    data2 = yaml.safe_load(file)

# Enter energies per atom of elements in the same order as yaml file
# ex. would go I, Rb, Sb for my material
reservoirEnergies = [-1.51496087, -0.988139613, -4.06064045]

#Place these in same order as vAtoms File
elementNames = ['Rb', 'Sb', 'I']

E_f = 1.713596 # Fermi Energy (eV)
gap = 1.813 # Band Gap (eV)
stepSize = 0.01 # Size of Fermi Energy Step (eV)
iterations = gap/stepSize

graphValues = []
fermiEnergies = []
# For graph of all defects on one plot

# Plot Settings
ylimmax = 7
ylimmin = -9
xlimmax = gap
xlimmin = 0

column1 = []
column2 = []
column3 = []
column4 = []
standardDeviation = []

#sets delta V for bulk to 0, note: bulk must be in first slot otherwise formatting will be messed up
excelFile = [0]

nameTracker = -1
start = 0
last10 = 0
while(start <= len(data) - 2):
    j = start + 1
    
    defect_name = data.iloc[start, 1]
    defect_name = defect_name.replace('/', '')
    
  
    while(data.iloc[j,0] != "stop"):
        if(data.iloc[j,0] != "nan"):        
            column1.append(float(data.iloc[j,0]))
            column2.append(float(data.iloc[j,1]))
            column3.append(float(data.iloc[j,2]))
            column4.append(float(data.iloc[j,3]))
        j = j + 1
    
    title = "vAtoms for " + defect_name
    
    #Everything here is used to plot/save the plot
    
    # plt.figure(figsize=(10,6))
    # plt.title(title)
    # plt.xlabel("Radial Distance (bohr)")
    # plt.ylabel("Energy (eV)")
    # plt.scatter(column1, column2, label = "V(long-range)")
    # plt.scatter(column1, column3, label = "V(defect)-V(ref)")
    # plt.scatter(column1, column4, label = "V(defect)-V(ref)-V(long-range)")
    # plt.legend(loc = 'upper left')
    # saveLocation = saveFolderNameVAtoms + "/" + str(title) + ".png"
    # plt.savefig(saveLocation)
    # plt.show()
    
    dict = {'distance': column1, 'values': column4}
    sortedData = pd.DataFrame(dict, dtype=float)
    sortedData = sortedData.sort_values(by = "distance", ascending = False)
    
    for i in range(0, 10):
        last10 = last10 + float(sortedData.iloc[i,1])
        standardDeviation.append(float(sortedData.iloc[i,1]))
        
    #Formats line to print nicely Note: prints element name and delta V value
    line_new = '{:<12}  {:>6}'.format(defect_name, str(round(last10/10,5)))
    print(line_new)
    print(np.std(standardDeviation))
    
    excelFile.append(last10/10)
    column1 = []
    column2 = []
    column3 = []
    column4 = []
    standardDeviation = []
    last10 = 0
    start = j

#Sets charge value for bulk state, requires bulk in first line of energies_corr file
charges = [0]
defectNames = ["bulk"]

#Seperates chare value into seperate column
for i in range(1, len(finalFile)):
    defectName = finalFile.iloc[i,0]
    defectName = defectName.replace('/', '')
    
    newName = ""
    
    j = 0
    while(defectName[j] != '_'):
        newName = newName + defectName[j]
        j = j + 1
    newName = newName + defectName[j]
    j = j + 1
    while(defectName[j] != '_'):
        newName = newName + defectName[j]
        j = j + 1
    j = j + 1
    charge = ""
    
    while(j < len(defectName)):
        charge = charge + str(defectName[j])
        j = j + 1
        
    charges.append(float(charge))
    defectNames.append(newName)

#Formats data into one file
finalFile = finalFile.drop(finalFile.columns[0], axis = 1)
finalFile.insert(0, "Defect Name", defectNames, True)
finalFile.insert(1, "Charge", charges, True)    
finalFile.insert(4, "delta V", excelFile, True)
finalFile.to_csv('energies_final.csv', index = False)

del (elementNames, charges, defectNames, column1, column2, column3, column4, last10, start, newName, i, j, title, nameTracker, excelFile)

energies_final = pd.read_csv(r".\energies_final.csv")

bulkEnergy = float(energies_final.iloc[0,2])

count = 0

# Generates all Fermi Energies for Plot
for i in range(0, int(iterations)):
    fermiEnergies.append(stepSize*i)
   
# Gets the name of the first defect for plots
storedName = energies_final.iloc[1,0]

# Function to format labels with subscript
def format_label(label):
    base, subscript = label.split('_')
    return f"{base}$_{{{subscript}}}$"

counter1 = 0
counter2 = 0    

elements = []
chemPot = []

for x in data2:
    if (counter1 > 0):
        for y in data2[x]:
            if (counter2 < 1):
                for z in data2[x][y]:
                    elements.append(z)
                    chemPot.append(data2[x][y][z])
            counter2 = counter2 + 1
    counter1 = counter1 + 1
    counter2 = 0
    
del (x, y, z, counter1, counter2)    

numOfElements = 0
tempArray = []
tempValue = 0

for i in range (0,len(elements)):
    for j in range (0, len(tempArray)):
        if(tempArray[j] == elements[i]):
            tempValue = tempValue + 1
    if (tempValue == 0):
        tempArray.append(elements[i])
        
numOfElements = len(tempArray)

del (i, j, tempArray, tempValue)

for i in range(0, int(len(elements)/numOfElements)):
    elementNames = []
    elementEPA = []
    
    for j in range(0, numOfElements):
        elementNames.append(str(elements[3*i + j]))
        elementEPA.append(float(chemPot[3*i + j]) + reservoirEnergies[j])
    
    print(elementNames)
    print(elementEPA)
    
    completeGraph = []
    namesArray = []
    
    for i in range (1, len(energies_final)):
        bulkDefectEnergy = float(energies_final.iloc[i,2])
        
        defectName = energies_final.iloc[i,0]
        
        j = 0
        firstElement = ""
        secondElement = ""
        
        # Gets the name of the first element
        while(defectName[j] != "_"):
            firstElement = firstElement + defectName[j]
            j = j + 1
            
        j = j + 1
        
        # Gets the name of the second element
        while(j != len(defectName)):
            secondElement = secondElement + defectName[j]
            j = j + 1

        finalDefectEnergy = bulkDefectEnergy - bulkEnergy 
        
        # Calculates 
        for k in range(0, len(elementNames)):
            # Subtract Energy From "Added" Element
            if(firstElement == elementNames[k]):
                finalDefectEnergy = finalDefectEnergy - elementEPA[k]
                print(elementNames[k])
            
            # Add Energy From "Subtracted" Element
            if(secondElement == elementNames[k]):
                finalDefectEnergy = finalDefectEnergy + elementEPA[k]
                print(elementNames[k])
        q = int(energies_final.iloc[i, 1])
        V = float(energies_final.iloc[i, 4])
        correction = float(energies_final.iloc[i, 3])
        
        # Account for Charge Defect and Correction Values
        finalDefectEnergy = finalDefectEnergy + q*(E_f + V) + correction
        energy = '{:<12}  {:>6}'.format(defectName + "_" + str(q), str(round(finalDefectEnergy,5)))
        print(energy)
        
        if(storedName != defectName and i != 1):
             tempArray = [] 
             forGraph = []
             
             # Appends minimum defect energy at each fermi energy
             for m in range (0, int(len(graphValues)/count)):
                 for n in range (0, count):
                     tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
                 forGraph.append(min(tempArray))
                 completeGraph.append(forGraph[m])
                 tempArray = []
                
             #Plots the individual charge defect plots
             # formattedTitle = format_label(str(storedName))
             # plt.figure(figsize=(10,6))
             # plt.title("Defect Plot of " + formattedTitle)
             # plt.xlabel("Fermi Energy (eV)")
             # plt.ylabel("Defect Energy (eV)")
             # plt.plot(fermiEnergies, forGraph)
             # plt.xlim(xlimmin, xlimmax)
             # plt.ylim(ylimmin, ylimmax)
             # saveLocation = saveFolderNameCharge + "/" + str(storedName) + ".png"
             # plt.savefig(saveLocation)
             # plt.show()
            
             namesArray.append(storedName)
             storedName = defectName
             
             # Clear Graph Values
             graphValues = []
             count = 0
        
        # Everything Below is for plotting defect energy vs fermi energy
        for k in range(0, int(iterations)):
            graphValues.append(finalDefectEnergy + q*stepSize*k) # Adds the total fermi energy multiplied by charge
        
        count = count + 1

    # Erases temporary data for last graph
    tempArray = [] 
    forGraph = []

    for m in range (0, int(len(graphValues)/count)):
        for n in range (0, count):
            tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
        forGraph.append(min(tempArray))
        completeGraph.append(forGraph[m])
        tempArray = []

    # This plots the last individual defect
    plt.figure(figsize=(10,6))
    storedName = defectName
    namesArray.append(storedName)
    
    # formattedTitle = format_label(str(storedName))
    # plt.title("Defect Plot of " + formattedTitle)
    # plt.xlabel("Fermi Energy (eV)")
    # plt.ylabel("Defect Energy (eV)")
    # plt.plot(fermiEnergies, forGraph, label = str(q))
    # plt.xlim(xlimmin, xlimmax)
    # plt.ylim(ylimmin, ylimmax)
    # saveLocation = saveFolderNameCharge + "/" + str(storedName) + ".png"
    # plt.savefig(saveLocation)
    # plt.show()

    numberOfDefects = int(len(completeGraph)/len(fermiEnergies))

    plt.figure(figsize=(3.5,6))
    plt.title("Charge Defect Plot")
    plt.xlabel("Fermi Energy (eV)")
    plt.ylabel("Defect Energy (eV)")
    plt.xlim(xlimmin, xlimmax)
    plt.ylim(ylimmin, ylimmax)

    # Format the labels in namesArray
    formatted_labels = [format_label(label) for label in namesArray]

    for i in range(0, numberOfDefects):
        tempData = []
        for j in range (0, int(len(fermiEnergies))):
            tempData.append(completeGraph[i*len(fermiEnergies) + j])
        
        plt.plot(fermiEnergies, tempData, label=formatted_labels[i])

    plt.legend()
    saveLocation = saveFolderNameCharge + "/" + "combinedDefects.png"
    plt.savefig(saveLocation)
    plt.show()
    
    del (elementNames, elementEPA, completeGraph, namesArray)

del(defectName, defect_name, dict, iterations,i, j, k, line_new, saveFolderNameCharge, tempData, tempArray, 
    V, xlimmax, xlimmin, ylimmax, ylimmin, standardDeviation, secondElement, firstElement, formatted_labels, file,
    saveLocation, stepSize, storedName, m, n, q, forGraph, sortedData, correction, charge, count, energy, fermiEnergies,
    finalDefectEnergy, finalFile, bulkDefectEnergy, saveFolderNameVAtoms)