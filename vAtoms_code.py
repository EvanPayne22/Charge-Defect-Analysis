# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 15:38:29 2024

@author: evanp
"""

import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import os

if not os.path.exists("vAtomsImages"):
    os.mkdir("vAtomsImages")

data = pd.read_csv(r".\vAtoms_output.csv").astype(str)
finalFile = pd.read_csv(r"./correctionEnergies.csv")

column1 = []
column2 = []
column3 = []
column4 = []
standardDeviation = []

#sets delta V for bulk to 0
excelFile = [0]

elementNames = ['Rb', 'Sb', 'I']

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
    
    plt.figure(figsize=(10,6))
    plt.title(title)
    plt.xlabel("Radial Distance (bohr)")
    plt.ylabel("Energy (eV)")
    plt.scatter(column1, column2, label = "V(long-range)")
    plt.scatter(column1, column3, label = "V(defect)-V(ref)")
    plt.scatter(column1, column4, label = "V(defect)-V(ref)-V(long-range)")
    plt.legend(loc = 'upper left')
    saveLocation = "vAtomsImages/" + str(title) + ".png"
    plt.savefig(saveLocation)
    plt.show()
    
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

charges = [0]
defectNames = ["bulk"]

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

finalFile = finalFile.drop(finalFile.columns[0], axis = 1)
finalFile.insert(0, "Defect Name", defectNames, True)
finalFile.insert(1, "Charge", charges, True)    
finalFile.insert(4, "delta V", excelFile, True)
finalFile.to_csv('energies_final.csv', index = False)
