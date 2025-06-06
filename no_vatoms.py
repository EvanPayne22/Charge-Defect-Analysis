# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 18:02:31 2024

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
import math

parser = argparse.ArgumentParser(description="Arguments for charge defect ",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-plotsingledefect", nargs='?', type=bool, default = False, help="plots the vAtoms plots")
parser.add_argument("-poscar", nargs='?', default = "./POSCAR", help="poscar file location, POSCAR is used to determine number of defect sites so use a version that includes all defects you are looking at")
parser.add_argument("-energiesFinal", nargs='?', default = "./energies_final.csv", help="energies and defect names file location")
parser.add_argument("-chempot", nargs='?', default = "./target_vertices.yaml", help="chemical potential file location (.yaml)")
parser.add_argument("-ymax", nargs='?', type=float, default = 7, help="ymax for defect graph")
parser.add_argument("-xmax", nargs='?', type=float, default = -3, help="xmax for defect graph")
parser.add_argument("-ymin", nargs='?', type=float, default = -7, help="ymin for defect graph")
parser.add_argument("-xmin", nargs='?', type=float, default = 0, help="xmin for defect graph")
parser.add_argument("-testfe", nargs='?', type=float, default = -1, help="displayes Q information at specified fermi energy")
parser.add_argument("-hse", nargs=2, type=float, help="enter in values for band gap and VBM for HSE calculation to generate PBE 'prediction'")
parser.add_argument("-kT", nargs='?', type=float, default = 0.05, help="kT value")
parser.add_argument("-printQ", nargs='?', type=bool, default = False, help="prints Q values of all defects at intrinsic fermi level")
parser.add_argument("bg", type=float, help="Band Gap")
parser.add_argument("vbm", type=float, help="VBM Offset")
parser.add_argument("resen", nargs='+', type=float, help="energy per atom of bulk atoms in same order as yaml file")
args = parser.parse_args()
config = vars(args)

if(config['xmax'] == -3):
    config['xmax'] = config['bg']

# Folder Name of Save Location for charge defect plots
saveFolderNameCharge = "defectAll"

# Creates Folder if it does not exist
if not os.path.exists(saveFolderNameCharge):
    os.mkdir(saveFolderNameCharge)

#Insert all files below
#Chem Potentials File
with open(config["chempot"], 'r') as file:
    data2 = yaml.safe_load(file)

poscar = config["poscar"]

f = open(poscar)
POSCAR = f.readlines()

elementNamesSeperate = POSCAR[5].split()
print(elementNamesSeperate)

defectSites = POSCAR[6].split()
for i in range(0, len(defectSites)):
    defectSites[i] = int(defectSites[i])

factor = math.gcd(*defectSites)

for i in range(0, len(defectSites)):
    defectSites[i] = defectSites[i]/factor

# Enter energies per atom of elements in the same order as yaml file
# ex. would go I, Rb, Sb for my material
reservoirEnergies = config["resen"]
#-1.84406847/2, -5.51085172/8, -7.89207833/2

colors = ["red", "green", "blue", "xkcd:saffron"]
lineStyles = ["solid", (0, (5, 7)), "dotted", "dashed"]
E_f = config['vbm'] # Fermi Energy (eV)
gap = config['bg'] # Band Gap (eV)

if(config["hse"] != None):
    originalVBM = E_f
    originalGap = gap
    
    E_f = config["hse"][1]
    gap = config["hse"][0]
    
    config['xmax'] = gap
    
stepSize = 0.0001 # Size of Fermi Energy Step (eV)
iterations = gap/stepSize

graphValues = []
minCharge = []
fermiEnergies = []
# For graph of all defects on one plot

# Plot Settings
ylimmax = config['ymax']
ylimmin = config['ymin']
xlimmax = config['xmax']
xlimmin = config['xmin']

energies_final = pd.read_csv(config["energiesFinal"])

bulkEnergy = float(energies_final.iloc[0,2])

count = 0

# Generates all Fermi Energies for Plot
for i in range(0, int(iterations)):
    fermiEnergies.append(stepSize*i)
   
# Gets the name of the first defect for plots
storedName = energies_final.iloc[1,0]

# Variable for determining number of spots
oldElement = " " 

# Function to format labels with subscript
def format_label(label):
    base, subscript = label.split('_')
    return f"{base}$_{{{subscript}}}$"

#Counters used for reading yaml file
counter1 = 0
counter2 = 0    

elements = [] #Element names in yaml file, should match the POSCAR given above
chemPot = [] #Stores the delta mu values needed to solve for chemical stability

#Reading yaml file to determine chemical potential values for each element
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

#Declartion of variables/arrays fro charge neutrality plot
numOfElements = 0 #Counts the number of "unique" elements
tempArray = [] #Used to calculate number of elements
tempValue = 0 #Used to calculate number of elements
allValues = [] #Stores all of the defect formation energies calculated below at each fermi level
allCharges = [] #Stores the charge state for each fermi level and defect
colorName = [] #Used to keep color coding for the plot
degenArray = [] #Array that stores the number of degeneracy states in supercell/primitive cell
finalColorNames = [] #Used to keep color coding for the plot

#Determing the number of unique elements
for i in range (0,len(elements)):
    for j in range (0, len(tempArray)):
        if(tempArray[j] == elements[i]):
            tempValue = tempValue + 1
    if (tempValue == 0):
        tempArray.append(elements[i])
        
numOfElements = len(tempArray)

del (i, j, tempArray, tempValue)

#Large for loop that will calculate charge neutrality of system based on given chemical potential points given in .yaml file
for p in range(0, int(len(elements)/numOfElements)):
    oldIndex = 0 #Used to determine when charge state switches accross fermi levels
    elementNames = []
    elementEPA = [] #Stores energy needed to add/subtract specific atom from defect
    
    lineStyleCount = [] #Used to ensure that all of the same color lines gave different line styles
    for i in range (0, len(colors)):
        lineStyleCount.append(0)
    
    for j in range(0, numOfElements):
        elementNames.append(str(elements[3*p + j]))
        elementEPA.append(float(chemPot[3*p + j]) + reservoirEnergies[j])
    
    print(elementNames)
    print(elementEPA)

    #Declaration of arrays for charge neutrality plot
    completeGraph = [] #Stores defect energies for all of the defects across the fermi energies
    namesArray = [] #Stores the names of the defects
    completeMinCharge = [] #Stores minimum charge state for all of the defects across the fermi energies
    defectSpots = [] #Number of locations for a specific defect 
    
    for i in range (1, len(energies_final)):
        bulkDefectEnergy = float(energies_final.iloc[i,2])
        
        defectName = energies_final.iloc[i,0]
        
        j = 0
        firstElement = "" #stores the name of the first/added "element" in defect
        secondElement = "" #stores the name of the second/removed "second" in defect
        
        # Gets the name of the first/added element
        while(defectName[j] != "_"):
            firstElement = firstElement + defectName[j]
            j = j + 1
            
        j = j + 1
        
        # Gets the name of the second/removed element
        while(j != len(defectName)):
            secondElement = secondElement + defectName[j]
            j = j + 1
            
        if(oldElement == " "):
            oldElement = secondElement
        
        finalDefectEnergy = bulkDefectEnergy - bulkEnergy 
        
        # Calculates the defect energy at specific charge state
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
             #Temp Array Declarations all needed for the charge neutrality plot
             tempArray = [] #Temp for charge states
             tempChargeArray = [] #Temp for charge states
             forGraph = [] #Temp for defect energies, merges tempArray
             forCharge = [] #Temp for charge states, merges tempChargeArray
             
             qw = 0 #used as a temp to determine color for plot
             feColor = "" #used as a temp to determine color for plot
             while(storedName[qw] != "_"):
                 feColor = feColor + storedName[qw]
                 qw += 1
                 
             colorName.append(feColor)
             
             if(len(finalColorNames) == 0):
                 finalColorNames.append(feColor)
             
             for bb in range (0, len(finalColorNames)):
                 if(feColor == finalColorNames[bb]):
                     break
                 elif(bb == len(finalColorNames) - 1):
                     finalColorNames.append(feColor)
             
             del(feColor, qw)
             
             for n in range (0, len(graphValues)):
                 allValues.append(graphValues[n])
                 allCharges.append(minCharge[n])
             
             # Appends minimum defect energy at each fermi energy
             for m in range (0, int(len(graphValues)/count)):
                 for n in range (0, count):
                     tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
                     tempChargeArray.append(minCharge  [m + int(len(minCharge)/count)*n])
                 forGraph.append(min(tempArray))
                 
                         
                 newIndex = tempArray.index(min(tempArray))
                 
                 forCharge.append(tempChargeArray[newIndex])
                 defectSpots.append(oldElement)
                     
                 if (newIndex != oldIndex):
                     oldIndex = newIndex
                     if(m != 0):
                         print("Transition from", forCharge[m - 1], "to", forCharge[m], "at", round(fermiEnergies[m], 5), "eV")
                                                  
                 completeGraph.append(forGraph[m])
                 completeMinCharge.append(forCharge[m])
                 tempArray = []
                 tempChargeArray = []
                
             #Plots the individual charge defect plots, contains all of the charge states for an individual defect spanned across entire band gap
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
             oldElement = secondElement
             
             # Clear Graph Values
             graphValues = []
             minCharge = []
             count = 0
        
        # Account for Charge Defect and Correction Values
        finalDefectEnergy = finalDefectEnergy + q*(E_f + V) + correction
        energy = '{:<12}  {:>6}'.format(defectName + "_" + str(q), str(round(finalDefectEnergy,5)))
        print(energy)
        
        # Everything Below is for plotting defect energy vs fermi energy
        for k in range(0, int(iterations)):
            graphValues.append(finalDefectEnergy + q*stepSize*k) # Adds the total fermi energy multiplied by charge
            minCharge.append(q)
        
        count = count + 1

    # Erases temporary data for last graph
    tempArray = [] 
    forGraph = []
    forCharge = []
    tempChargeArray = []

    #Everything below repeats above for the last defect, until noted
    qw = 0
    feColor = ""
    while(storedName[qw] != "_"):
        feColor = feColor + storedName[qw]
        qw += 1
        
    colorName.append(feColor)
    
    if(len(finalColorNames) == 0):
        finalColorNames.append(feColor)
    
    for bb in range (0, len(finalColorNames)):
        if(feColor == finalColorNames[bb]):
            break
        elif(bb == len(finalColorNames) - 1):
            finalColorNames.append(feColor)
    
    del(feColor, qw)
    
    for n in range (0, len(graphValues)):
        allValues.append(graphValues[n])
        allCharges.append(minCharge[n])
    
    for m in range (0, int(len(graphValues)/count)):
        for n in range (0, count):
            tempArray.append(graphValues[m + int(len(graphValues)/count)*n])
            tempChargeArray.append(minCharge[m + int(len(minCharge)/count)*n])
        forGraph.append(min(tempArray))
        
        newIndex = tempArray.index(min(tempArray))
        
        forCharge.append(tempChargeArray[newIndex])
        defectSpots.append(oldElement)
        
        if (newIndex != oldIndex):
            oldIndex = newIndex
            if(m != 0):
                print("Transition from", forCharge[m - 1], "to", forCharge[m], "at", round(fermiEnergies[m], 5), "eV")
        
        completeGraph.append(forGraph[m])
        completeMinCharge.append(forCharge[m])
        tempArray = []
        tempChargeArray = []
    # This is the last of the repeated analysis
  
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
    # plt.title("Charge Defect Plot")
    plt.xlabel("Fermi Energy (eV)")
    plt.ylabel("Defect Energy (eV)")
    plt.xlim(xlimmin, xlimmax)
    plt.ylim(ylimmin, ylimmax)
    
    print("")

    #Below contains calculations to determine the charge neutrality of the system
    temp1 = [] #Contains the defect energy of each defect at each fermi energy
    temp2 = 0 #currect fermi energy being analyzed
    temp3 = [] #Contains the minimum charge states
    temp4 = [] #Contains the number of possible degeneracy states for the type of defect, obtained from original POSCAR
    sign1 = False #Temps used to determine if the charge of the whole system flips
    sign2 = False #Temps used to determine if the charge of the whole system flips
    Q = 0 #Temps used to determine if the charge of the whole system flips
    kT = config['kT'] #specfied boltzmann * temp value
    e = 2.718 #exp value
    qArray = [] #stores all Q values, and is used to see if charge of system changes
    qValue = 0 #fermi energy value stored to print when sign changes
    #Determines intrinsic fermi level of defects
    for i in range(0, int(iterations)):
        qArray = []
        temp2 = float("{:0.4f}".format(fermiEnergies[i]))
        for j in range(0, numberOfDefects):
            temp1.append("{:0.7f}".format(completeGraph[i + j*int(iterations)]))
            temp3.append(completeMinCharge[i + j*int(iterations)])
            temp4.append(defectSpots[i + j*int(iterations)])
            
            q_i = int(temp3[j])
            
            for k in range(0, len(elementNamesSeperate)):
                # Subtract Energy From "Added" Element
                if(temp4[j] == elementNamesSeperate[k]):
                    N_i = defectSites[k]
                                                    
            Q = Q + N_i*q_i*(e**(-1 * float(temp1[j]) / (kT))) #Calculates total Q value at fermi energy
            
            if(float(config['testfe']) == float("{:0.4f}".format(fermiEnergies[i]))):
                print("charge state of defect", j, "=", q_i)
                print("degeneracy states of defect", j, "=", N_i)
                print("formation energy of defect", j, "=", temp1[j])
                print()
        
            qArray.append(Q)
                
        if(Q > 0):
            sign1 = True
        else:
            sign1 = False
        
        if(i != 0 and sign2 != sign1):
            print()
            print("Intrinisc Fermi Defect Level: " + "{:0.4f}".format(temp2) + " eV")
            print()
            if(config['printQ']):
                tempQ = 0 
                for k in range(0, numberOfDefects):
                    tempQ = qArray[k] - tempQ 
                    print("Q value of defect", k, "=", tempQ)
                print("")
                print("Total Q Value =", Q)
                print("")
                del(tempQ)
            qValue = temp2
                    
        if(config["testfe"] == float("{:0.4f}".format(fermiEnergies[i]))):
            print("Q value =", Q)
            print()
        
        sign2 = sign1
        
        temp1 = []
        temp3 = []
        temp4 = []
        Q = 0
        
        
        
    
    if(config["hse"] != None):
        plt.fill([xlimmin, xlimmin, originalVBM - E_f, originalVBM - E_f], [ylimmin, ylimmax, ylimmax, ylimmin], color = "silver")
        plt.fill([xlimmax, xlimmax, originalVBM - E_f + originalGap, originalVBM - E_f + originalGap], [ylimmin, ylimmax, ylimmax, ylimmin], color = "silver")

    # Format the labels in namesArray
    formatted_labels = [format_label(label) for label in namesArray]

    for i in range(0, numberOfDefects):
        tempData = []
        for j in range (0, int(len(fermiEnergies))):
            tempData.append(completeGraph[i*len(fermiEnergies) + j])
        
        for j in range(0, len(finalColorNames)):
            if(colorName[i] == finalColorNames[j]):
        
                plt.plot(fermiEnergies, tempData, label=formatted_labels[i], color = colors[j], linestyle = lineStyles[lineStyleCount[j] % len(lineStyles)])
                lineStyleCount[j] = lineStyleCount[j] + 1
    plt.axvline(qValue, color="black", linestyle="dashed")
    colNum = math.ceil(numberOfDefects/7)
    plt.legend(loc = 8, ncols = colNum)
    saveLocation = saveFolderNameCharge + "/" +  "combinedDefects" +  str(p + 1) + ".png"
    plt.savefig(saveLocation)
    plt.show()
    
    namesArray = []
    storedName = energies_final.iloc[1,0]
    oldElement = " "
    
    colorName = []
 
    del (elementNames, elementEPA, completeGraph, namesArray)
#removes unneccesary variables to make it easier to read values on spyder or other ide
del(allCharges, allValues, args, bb, bulkDefectEnergy, chemPot, colNum, colorName, colors, completeMinCharge, config, correction, count, data2, defectName, defectSites, defectSpots, e, 
    elementNamesSeperate, elements, energies_final, energy, f, factor, fermiEnergies, file, finalColorNames, finalDefectEnergy, firstElement, forCharge, forGraph, 
    formatted_labels, graphValues, i, iterations, j, k, lineStyleCount, lineStyles, m, minCharge, n, N_i, newIndex, numOfElements, oldElement, oldIndex, oldQ, oldQ1, p, parser, poscar, POSCAR, q, Q, Q1, q_i,
    qValue, qArray, saveFolderNameCharge, saveLocation, secondElement, sign1, sign2, storedName, kT, temp1, temp2, temp3, temp4, tempArray, tempChargeArray, tempData, V, xlimmax, xlimmin, ylimmax, ylimmin)
