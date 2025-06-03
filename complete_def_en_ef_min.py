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
import math


#The lines below are tags for different settings and required arguments
parser = argparse.ArgumentParser(description="Arguments for charge defect ",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-plotsingledefect", nargs='?', type=bool, default = False, help="plots the vAtoms plots")
parser.add_argument("-plotvatoms", nargs='?', type=bool, default = False, help="plots the vAtoms plots")
parser.add_argument("-poscar", nargs='?', default = "./POSCAR", help="poscar file location, POSCAR is used to determine number of defect sites so use a version that includes all defects you are looking at")
parser.add_argument("-vatoms", nargs='?', default = "./vAtoms_output.csv", help="vatoms file location")
parser.add_argument("-correction", nargs='?', default = "./energies_correction.csv", help="energies and defect names file location")
parser.add_argument("-chempot", nargs='?', default = "./target_vertices.yaml", help="chemical potential file location (.yaml)")
parser.add_argument("-ymax", nargs='?', type=float, default = 7, help="ymax for defect graph")
parser.add_argument("-xmax", nargs='?', type=float, default = -3, help="xmax for defect graph")
parser.add_argument("-ymin", nargs='?', type=float, default = -7, help="ymin for defect graph")
parser.add_argument("-xmin", nargs='?', type=float, default = 0, help="xmin for defect graph")
parser.add_argument("-vatomsymax", nargs='?', type=float, default = -100, help="ymax for vatoms graph")
parser.add_argument("-vatomsxmax", nargs='?', type=float, default = -100, help="xmax for vatoms graph")
parser.add_argument("-vatomsymin", nargs='?', type=float, default = -100, help="ymin for vatoms graph")
parser.add_argument("-vatomsxmin", nargs='?', type=float, default = -100, help="xmin for vatoms graph")
parser.add_argument("-testfe", nargs='?', type=float, default = -1, help="displayes Q information at specified fermi energy")
parser.add_argument("-kT", nargs='?', type=float, default = 0.05, help="kT value")
parser.add_argument("-printQ", nargs='?', type=bool, default = False, help="prints Q values of all defects at intrinsic fermi level")
parser.add_argument("-percent", nargs='?', type=float, default = 0.8, help="value to determine amount of atoms averaged for delta v value using all atoms beyond specifed percent of furthest atom")
parser.add_argument("-number", nargs='?', type=int, default = -1, help="value to determine amount of atoms averaged for delta v value using the furthest specified number of atoms")
parser.add_argument("-hse", nargs=2, type=float, help="enter in values for band gap and VBM for HSE calculation to generate PBE 'prediction'")
parser.add_argument("bg", type=float, help="Band Gap")
parser.add_argument("vbm", type=float, help="VBM Offset")
parser.add_argument("resen", nargs='+', type=float, help="energy per atom of bulk atoms in same order as yaml file")
args = parser.parse_args()
config = vars(args)

#This sets the limit for the charge neutrality plot to band gap as a default value
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


#This reads in a POSCAR from the directory, this should include information on all of the possible atom sites as well as atom names
#Example is given in the repository
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

#This is a list of oclors and line styles used for the charge neutrailty plot, colors and styles could be added/subtracted from arrays below
colors = ["red", "green", "blue", "orange"]
lineStyles = ["solid", (0, (5, 7)), "dotted", "dashdot", "dashed"]
E_f = config['vbm'] # Fermi Energy (eV)
gap = config['bg'] # Band Gap (eV)

#This determines if the hse tag was set to T/F and adjusts calues accordingly
if(config["hse"] != None):
    originalVBM = E_f
    originalGap = gap
    
    E_f = config["hse"][1]
    gap = config["hse"][0]
    
    config['xmax'] = gap

#This is the number of steps (or the level of detail) for the charge neutrality plot
stepSize = 0.0001 # Size of Fermi Energy Step (eV)
iterations = gap/stepSize

#Declaration of arrays for charge neutrality plot
graphValues = [] #Values stored for plot, used as a temp to analyze lowest energy charge state
minCharge = [] #Array that stores the minimum charge at given "fermi energy"
fermiEnergies = [] #Array that contains "x" values, based on the number of steps set above

# Plot Settings - set with tags shown above
ylimmax = config['ymax']
ylimmin = config['ymin']
xlimmax = config['xmax']
xlimmin = config['xmin']

#Array declarations to read in energies_correction file.
column1 = []
column2 = []
column3 = []
column4 = []
standardDeviation = []
allDev = [0]

#sets delta V for bulk to 0, note: bulk must be in first slot otherwise formatting will be messed up
excelFile = [0]

#This section calculates the correction values needed to account for the assumed gaussian decay
nameTracker = -1 #Used to read defect name
start = 0 #Starting line value which changes after a new defect is being read in the vAtoms output file
last10 = 0 #Variable used to average out the "last 10" atoms furthest from defect. This won't be the last 10 depending on the value set in tags
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
        
        delV = last10/i #Averaing the deviation of the furthest atoms to determine correction value
    else:
        value = config["number"] - 1
        minDistance = float(sortedData.iloc[value,0])
               
        for a in range(0, config["number"]):
            last10 = last10 + float(sortedData.iloc[a,1])
            standardDeviation.append(float(sortedData.iloc[a,1]))
            
            i = a
        
        delV = last10/config["number"]
    
    #Everything here is used to plot/save the vatoms plot if plotvatoms tag is set
    if(config["plotvatoms"] == True):
        
        plt.figure(figsize=(10,6))
        
        plt.title(title)
        plt.xlabel("Radial Distance (bohr)")
        plt.ylabel("Energy (eV)")
        plt.scatter(column1, column2, label = "V(long-range)")
        plt.scatter(column1, column3, label = "V(defect)-V(ref)")
        plt.scatter(column1, column4, label = "V(defect)-V(ref)-V(long-range)")
        
        if(config["vatomsxmin"] != -100):
            xmin = config["vatomsxmin"]
        else:
            xmin = 0
        
        if(config["vatomsxmax"] != -100):
            xmax = config["vatomsxmax"]
        else:
            xmax = sortedData.iloc[0,0] + 1
            
        if(config["vatomsymin"] != -100):
            ymin = config["vatomsymin"]
        else:
            ymin = plt.ylim()[0]

        if(config["vatomsymax"] != -100):
            ymax = config["vatomsymax"]
        else:
            ymax = plt.ylim()[1]
            
        plt.xlim(xmin, xmax)
        plt.ylim(ymin, ymax)
        plt.plot([sortedData.iloc[i,0], xmax], [delV, delV], color = 'black', linestyle = "dashed")
        plt.plot([sortedData.iloc[i,0], sortedData.iloc[i,0]], [ymin, delV], color = 'black', linestyle = "dashed")
        
        plt.legend(loc = 'upper right')
        saveLocation = saveFolderNameVAtoms + "/" + str(title) + ".png"
        plt.savefig(saveLocation)
        plt.show()
        plt.close()
        
    #Formats line to print nicely Note: prints element name and delta V value
    line_new = '{:<12}  {:>6}'.format(defect_name, str(round(delV, 5)))
        
    print(line_new)
    print(np.std(standardDeviation))
    
    allDev.append(np.std(standardDeviation))
       
    #Appending correction values to array and then clearing the columns to calculate for other defects
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

#Formats data into one file titled "energies_final.csv"
finalFile = finalFile.drop(finalFile.columns[0], axis = 1)
finalFile.insert(0, "Defect Name", defectNames, True)
finalFile.insert(1, "Charge", charges, True)    
finalFile.insert(4, "delta V", excelFile, True)
finalFile.insert(5, "Std Deviation", allDev, True)
finalFile.to_csv('energies_final.csv', index = False)

del (defectNames, column1, column2, column3, column4, last10, start, newName, i, j, title, nameTracker, excelFile)

energies_final = pd.read_csv(r"./energies_final.csv")

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
del(defectName, defect_name, dict, iterations,i, j, k, line_new, saveFolderNameCharge, tempData, tempArray, f, parser,
    V, xlimmax, xlimmin, ylimmax, ylimmin, standardDeviation, secondElement, firstElement, formatted_labels, file,
    saveLocation, stepSize, storedName, m, n, q, forGraph, sortedData, correction, charge, count, energy, fermiEnergies,
    finalDefectEnergy, finalFile, bulkDefectEnergy, saveFolderNameVAtoms, allDev, delV, oldIndex, newIndex, p, minDistance,
    completeMinCharge,  defectSpots, e, factor, forCharge, graphValues, minCharge, N_i, oldElement, Q, q_i, qArray,
    sign1, sign2, tempChargeArray, temp1, temp2, temp3, kT)

