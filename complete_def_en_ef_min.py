# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 13:15:19 2024

@author: evanp
========================================================================================
Input: vAtoms_output.csv, target_vertices.yaml, energies_correction.csv
Output: Charge Defect Plot with all defects at all specified points in .yaml file -- Optional: vAtoms plots and single defect plots
========================================================================================
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import yaml
import argparse

parser = argparse.ArgumentParser(description="Arguments for charge defect ",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-plotsingledefect", nargs='?', type=bool, default = False, help="plots the vAtoms plots")
parser.add_argument("-plotvatoms", nargs='?', type=bool, default = False, help="plots the vAtoms plots")
parser.add_argument("-poscar", nargs='?', default = "./POSCAR", help="poscar file location")
parser.add_argument("-vatoms", nargs='?', default = "./vAtoms_output.csv", help="vatoms file location")
parser.add_argument("-correction", nargs='?', default = "./energies_correction.csv", help="energies and defect names file location")
parser.add_argument("-chempot", nargs='?', default = "./target_vertices.yaml", help="chemical potential file location (.yaml)")
parser.add_argument("-ymax", nargs='?', type=float, default = 7, help="ymax for defect graph")
parser.add_argument("-xmax", nargs='?', type=float, default = -3, help="xmax for defect graph")
parser.add_argument("-ymin", nargs='?', type=float, default = -7, help="ymin for defect graph")
parser.add_argument("-xmin", nargs='?', type=float, default = 0, help="xmin for defect graph")
parser.add_argument("-percent", nargs='?', type=float, default = 0.8, help="value to determine amount of atoms averaged for delta v value using all atoms beyond specifed percent of furthest atom")
parser.add_argument("-number", nargs='?', type=int, default = -1, help="value to determine amount of atoms averaged for delta v value using the furthest specified number of atoms")
parser.add_argument("-hse", nargs=2, type=float, help="enter in values for band gap and VBM for HSE calculation to generate PBE 'prediction'")
parser.add_argument("bg", type=float, help="Band Gap")
parser.add_argument("vbm", type=float, help="VBM Offset")
parser.add_argument("resen", nargs='+', type=float, help="energy per atom of bulk atoms in same order as yaml file")
args = parser.parse_args()
config = vars(args)

if(config['xmax'] == -3):
    config['xmax'] = config['bg']

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
data = pd.read_csv(config["vatoms"]).astype(str)
#Initial Energies Data
finalFile = pd.read_csv(config["correction"])
#Chem Potentials File
with open(config["chempot"], 'r') as file:
    data2 = yaml.safe_load(file)

poscar = config["poscar"]

f = open(poscar)
POSCAR = f.readlines()

elementNames = POSCAR[5].split()
print(elementNames)

# Enter energies per atom of elements in the same order as yaml file
# ex. would go I, Rb, Sb for my material
reservoirEnergies = config["resen"]
#-1.84406847/2, -5.51085172/8, -7.89207833/2

E_f = config['vbm'] # Fermi Energy (eV)
gap = config['bg'] # Band Gap (eV)

if(config["hse"] != None):
    originalVBM = E_f
    originalGap = gap
    
    E_f = config["hse"][1]
    gap = config["hse"][0]
    
    config['xmax'] = gap
    
stepSize = 0.01 # Size of Fermi Energy Step (eV)
iterations = gap/stepSize

graphValues = []
fermiEnergies = []
# For graph of all defects on one plot

# Plot Settings
ylimmax = config['ymax']
ylimmin = config['ymin']
xlimmax = config['xmax']
xlimmin = config['xmin']

column1 = []
column2 = []
column3 = []
column4 = []
standardDeviation = []
allDev = [0]

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
    
    dict = {'distance': column1, 'values': column4}
    sortedData = pd.DataFrame(dict, dtype=float)
    sortedData = sortedData.sort_values(by = "distance", ascending = False)
    
    if(config["number"] < 0):
        minDistance = float(sortedData.iloc[0,0] * config["percent"])
        
        i = 0
        
        while(float(sortedData.iloc[i,0]) > minDistance):
            last10 = last10 + float(sortedData.iloc[i,1])
            standardDeviation.append(float(sortedData.iloc[i,1]))
            i = i + 1
        
        delV = last10/i
    else:
        value = config["number"] - 1
        minDistance = float(sortedData.iloc[value,0])
               
        for a in range(0, config["number"]):
            last10 = last10 + float(sortedData.iloc[a,1])
            standardDeviation.append(float(sortedData.iloc[a,1]))
            
            i = a
        
        delV = last10/config["number"]
    
    #Everything here is used to plot/save the plot
    
    if(config["plotvatoms"] == True):
        ymin = -0.3
        ymax = 0.3
        xmin = 0
        xmax = sortedData.iloc[0,0] + 1 
        plt.figure(figsize=(10,6))
        plt.plot([sortedData.iloc[i,0], xmax], [delV, delV], color = 'black', linestyle = "dashed")
        plt.plot([sortedData.iloc[i,0], sortedData.iloc[i,0]], [ymin, delV], color = 'black', linestyle = "dashed")
        plt.title(title)
        plt.xlabel("Radial Distance (bohr)")
        plt.ylabel("Energy (eV)")
        plt.scatter(column1, column2, label = "V(long-range)")
        plt.scatter(column1, column3, label = "V(defect)-V(ref)")
        plt.scatter(column1, column4, label = "V(defect)-V(ref)-V(long-range)")
        plt.legend(loc = 'upper left')
        saveLocation = saveFolderNameVAtoms + "/" + str(title) + ".png"
        plt.savefig(saveLocation)
        plt.show()
        plt.close()
        
    #Formats line to print nicely Note: prints element name and delta V value
    line_new = '{:<12}  {:>6}'.format(defect_name, str(round(delV, 5)))
        
    print(line_new)
    print(np.std(standardDeviation))
    
    allDev.append(np.std(standardDeviation))
       
    excelFile.append(delV)
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
finalFile.insert(5, "Std Deviation", allDev, True)
finalFile.to_csv('energies_final.csv', index = False)

del (elementNames, charges, defectNames, column1, column2, column3, column4, last10, start, newName, i, j, title, nameTracker, excelFile)

energies_final = pd.read_csv(r"./energies_final.csv")

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

for p in range(0, int(len(elements)/numOfElements)):
    oldIndex = 0
    elementNames = []
    elementEPA = []
    
    for j in range(0, numOfElements):
        elementNames.append(str(elements[3*p + j]))
        elementEPA.append(float(chemPot[3*p + j]) + reservoirEnergies[j])
    
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
            
            # Add Energy From "Subtracted" Element
            if(secondElement == elementNames[k]):
                finalDefectEnergy = finalDefectEnergy + elementEPA[k]
        q = int(energies_final.iloc[i, 1])
        V = float(energies_final.iloc[i, 4])
        correction = float(energies_final.iloc[i, 3])
        
        if(storedName != defectName and i != 1):
             tempArray = [] 
             forGraph = []
             
             # Appends minimum defect energy at each fermi energy
             for m in range (0, int(len(graphValues)/count)):
                 for n in range (0, count):
                     tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
                 forGraph.append(min(tempArray))
                 
                 newIndex = tempArray.index(min(tempArray))
                     
                 if (newIndex != oldIndex):
                     oldIndex = newIndex
                     if(m != 0):
                         print(fermiEnergies[m])
                                                  
                 completeGraph.append(forGraph[m])
                 tempArray = []
                
             #Plots the individual charge defect plots
             if(config["plotsingledefect"] == True): 
                 formattedTitle = format_label(str(storedName))
                 plt.figure(figsize=(10,6))
                 plt.title("Defect Plot of " + formattedTitle)
                 plt.xlabel("Fermi Energy (eV)")
                 plt.ylabel("Defect Energy (eV)")
                 plt.plot(fermiEnergies, forGraph)
                 plt.xlim(xlimmin, xlimmax)
                 plt.ylim(ylimmin, ylimmax)
                 saveLocation = saveFolderNameCharge + "/" + str(storedName) + ".png"
                 plt.savefig(saveLocation)
                 plt.show()
            
             namesArray.append(storedName)
             storedName = defectName
             
             # Clear Graph Values
             graphValues = []
             count = 0
        
        # Account for Charge Defect and Correction Values
        finalDefectEnergy = finalDefectEnergy + q*(E_f + V) + correction
        energy = '{:<12}  {:>6}'.format(defectName + "_" + str(q), str(round(finalDefectEnergy,5)))
        print(energy)
        
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
        
        newIndex = tempArray.index(min(tempArray))
            
        if (newIndex != oldIndex):
            oldIndex = newIndex
            if(m != 0):
                print(fermiEnergies[m])
        
        completeGraph.append(forGraph[m])
        tempArray = []

    # This plots the last individual defect
    plt.figure(figsize=(10,6))
    storedName = defectName
    namesArray.append(storedName)
    
    if(config["plotsingledefect"] == True): 
        formattedTitle = format_label(str(storedName))
        plt.title("Defect Plot of " + formattedTitle)
        plt.xlabel("Fermi Energy (eV)")
        plt.ylabel("Defect Energy (eV)")
        plt.plot(fermiEnergies, forGraph, label = str(q))
        plt.xlim(xlimmin, xlimmax)
        plt.ylim(ylimmin, ylimmax)
        saveLocation = saveFolderNameCharge + "/" + str(storedName) + ".png"
        plt.savefig(saveLocation)
        plt.show()

    numberOfDefects = int(len(completeGraph)/len(fermiEnergies))

    plt.figure(figsize=(5,7))
    plt.title("Charge Defect Plot")
    plt.xlabel("Fermi Energy (eV)")
    plt.ylabel("Defect Energy (eV)")
    plt.xlim(xlimmin, xlimmax)
    plt.ylim(ylimmin, ylimmax)
    
    if(config["hse"] != None):
        plt.fill([xlimmin, xlimmin, originalVBM - E_f, originalVBM - E_f], [ylimmin, ylimmax, ylimmax, ylimmin], color = "silver")
        plt.fill([xlimmax, xlimmax, xlimmax - (gap - originalGap), xlimmax - (gap - originalGap)], [ylimmin, ylimmax, ylimmax, ylimmin], color = "silver")

    # Format the labels in namesArray
    formatted_labels = [format_label(label) for label in namesArray]

    for i in range(0, numberOfDefects):
        tempData = []
        for j in range (0, int(len(fermiEnergies))):
            tempData.append(completeGraph[i*len(fermiEnergies) + j])
        
        plt.plot(fermiEnergies, tempData, label=formatted_labels[i])

    plt.legend(loc = 8, ncols = 2)
    saveLocation = saveFolderNameCharge + "/" +  "combinedDefects" +  str(p + 1) + ".png"
    plt.savefig(saveLocation)
    plt.show()
    
    namesArray = []
    storedName = energies_final.iloc[1,0]
    
    #del (elementNames, elementEPA, completeGraph, namesArray)

del(defectName, defect_name, dict, iterations,i, j, k, line_new, saveFolderNameCharge, tempData, tempArray, f, parser,
    V, xlimmax, xlimmin, ylimmax, ylimmin, standardDeviation, secondElement, firstElement, formatted_labels, file,
    saveLocation, stepSize, storedName, m, n, q, forGraph, sortedData, correction, charge, count, energy, fermiEnergies,
    finalDefectEnergy, finalFile, bulkDefectEnergy, saveFolderNameVAtoms, allDev, delV, oldIndex, newIndex, p, namesArray, minDistance)
