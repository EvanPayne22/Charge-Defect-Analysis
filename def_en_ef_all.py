# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 17:32:06 2024

@author: evanp
========================================================================================
Input: energies_final.csv from vAtoms_code.csv, ./target_vertices.yaml, 
in commandline - bg, vbm, and resevoir energies
Output: Charge defect plot for individual defects that includes all charge state lines
========================================================================================
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import yaml
import argparse

parser = argparse.ArgumentParser(description="Arguments for charge defect ",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-poscar", nargs='?', default = "./POSCAR", help="poscar file location")
parser.add_argument("-vatoms", nargs='?', default = "./vAtoms_output.csv", help="vatoms file location")
parser.add_argument("-correction", nargs='?', default = "./energies_final.csv", help="energies and defect names file location")
parser.add_argument("-chempot", nargs='?', default = "./target_vertices.yaml", help="chemical potential file location (.yaml)")
parser.add_argument("-ymax", nargs='?', type=float, default = 7, help="ymax for defect graph")
parser.add_argument("-xmax", nargs='?', type=float, default = -3, help="xmax for defect graph")
parser.add_argument("-ymin", nargs='?', type=float, default = -7, help="ymin for defect graph")
parser.add_argument("-xmin", nargs='?', type=float, default = 0, help="xmin for defect graph")
parser.add_argument("-hse", nargs=2, type=float, help="enter in values for band gap and VBM for HSE calculation to generate PBE 'prediction'")
parser.add_argument("bg", type=float, help="Band Gap")
parser.add_argument("vbm", type=float, help="VBM Offset")
parser.add_argument("resen", nargs='+', type=float, help="energy per atom of bulk atoms in same order as yaml file")
args = parser.parse_args()
config = vars(args)

#Folder Name of Save Location
saveFolderName = "chargeDefectsSeperated"

#Creates Folder if it does not exist
if not os.path.exists(saveFolderName):
    os.mkdir(saveFolderName)

testFile = pd.read_csv(config["correction"])

with open(config["chempot"], 'r') as file:
    data2 = yaml.safe_load(file)

counter1 = 0
counter2 = 0

#Energy per Atom of Elements
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

E_f = config['vbm'] # Fermi Energy (eV)
gap = config['bg'] # Band Gap (eV)
reservoirEnergies = config["resen"]

if(config["hse"] != None):
    originalVBM = E_f
    originalGap = gap
    
    E_f = config["hse"][1]
    gap = config["hse"][0]
    
    config['xmax'] = gap

stepSize = 0.01 #Size of Fermi Energy Step (eV)
iterations = gap/stepSize

bulkEnergy = float(testFile.iloc[0,2])

graphValues = []
fermiEnergies = []

# Function to format labels with subscript
def format_label(label):
    base, subscript = label.split('_')
    return f"{base}$_{{{subscript}}}$"

#Plot Settings
ylimmax = 7
ylimmin = -9
xlimmax = gap
xlimmin = 0

#Generates all Fermi Energies for Plot
for i in range(0, int(iterations)):
    fermiEnergies.append(stepSize*i)
   

for p in range(0, int(len(elements)/numOfElements)):
    #Needed for Plots
    storedName = testFile.iloc[1,0]
    
    elementNames = []
    elementEPA = []
    
    for j in range(0, numOfElements):
        elementNames.append(str(elements[3*p + j]))
        elementEPA.append(float(chemPot[3*p + j]) + reservoirEnergies[j])
    
    print(elementNames)
    print(elementEPA)
    
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
     
        plt.title("Defect Plot of " + format_label(defectName))
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
    
    graphValues = []     
