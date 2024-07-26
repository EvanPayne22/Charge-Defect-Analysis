# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 15:38:29 2024

@author: evanp
========================================================================================
Input: vAtoms_output.csv and energies_correction.csv, additionally parser arguments explained below
Output: energies_final.csv that contains deltaV values and standard deviation
========================================================================================
"""

import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import os
import argparse

if not os.path.exists("vAtomsImages"):
    os.mkdir("vAtomsImages")

parser = argparse.ArgumentParser(description="Arguments for sxdefect plots ",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-vatoms", nargs='?', default = "./vAtoms_output.csv", help="vatoms file location")
parser.add_argument("-correction", nargs='?', default = "./energies_correction.csv", help="energies and defect names file location")
parser.add_argument("-ymax", nargs='?', type=float, default = 0.3, help="ymax for defect graph")
parser.add_argument("-xmax", nargs='?', type=float, default = -1, help="xmax for defect graph")
parser.add_argument("-ymin", nargs='?', type=float, default = -0.3, help="ymin for defect graph")
parser.add_argument("-xmin", nargs='?', type=float, default = 0, help="xmin for defect graph")
parser.add_argument("-percent", nargs='?', type=float, default = 0.8, help="value to determine amount of atoms averaged for delta v value using all atoms beyond specifed percent of furthest atom")
parser.add_argument("-number", nargs='?', type=int, default = -1, help="value to determine amount of atoms averaged for delta v value using the furthest specified number of atoms")
args = parser.parse_args()
config = vars(args)

data = pd.read_csv(config["vatoms"]).astype(str)
finalFile = pd.read_csv(config["correction"])


column1 = []
column2 = []
column3 = []
column4 = []
allDev = []
standardDeviation = []
allDev = [0]

#sets delta V for bulk to 0
excelFile = [0]

elementNames = ['Te', 'Se', 'Cd']

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
    
    #Formats line to print nicely Note: prints element name and delta V value
    line_new = '{:<12}  {:>6}'.format(defect_name, str(round(delV, 5)))
        
    print(line_new)
    print(np.std(standardDeviation))
    allDev.append(np.std(standardDeviation))
    
    #Everything here is used to plot/save the plot
    ymin = config["ymin"]
    ymax = config["ymax"]
    xmin = config["xmin"]
    xmax = config["xmax"]
    if(xmax < 0):
        xmax = sortedData.iloc[0,0] + 1
    
    
    plt.figure(figsize=(10,6))
    plt.plot([sortedData.iloc[i,0], xmax], [delV, delV], color = 'black', linestyle = "dashed")
    plt.plot([sortedData.iloc[i,0], sortedData.iloc[i,0]], [ymin, delV], color = 'black', linestyle = "dashed")
    plt.ylim(ymin, ymax)
    plt.xlim(xmin, xmax)
    plt.title(title)
    plt.xlabel("Radial Distance (bohr)")
    plt.ylabel("Energy (eV)")
    plt.scatter(column1, column2, label = "V(long-range)")
    plt.scatter(column1, column3, label = "V(defect)-V(ref)")
    plt.scatter(column1, column4, label = "V(defect)-V(ref)-V(long-range)")
    plt.legend()
    saveLocation = "vAtomsImages/" + str(title) + ".png"
    plt.savefig(saveLocation)
    plt.show()
    
    excelFile.append(delV)
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
finalFile.insert(5, "std dev", allDev, True)
finalFile.to_csv('energies_final.csv', index = False)
