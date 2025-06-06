# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 00:52:18 2025

@author: aheib
"""

import matplotlib.pyplot as plt

#Function to format defect names with subscript
def format_label(label):
    base, subscript = label.split('_')
    return f"{base}$_{{{subscript}}}$"

data = r"./eigenVal.txt"

f = open(data)
eigenVal = f.readlines()

numberOfDefects = 0 #The number of defects being plotted

for i in range (0, len(eigenVal)):
    if (eigenVal[i][0] == 'd'): #Countes the Number of Defects Being Plotted
        numberOfDefects += 1
    eigenVal[i] = eigenVal[i].split()
    
    
count = 0 #Counter for reading eigenVal file
plotNum = 1 #Counter to store which sub plot data is stored for

energy = [] #Energy Level of the Defect in energy Gap
occupancy = [] #Occupancy of Defect States
dotSize = 100 #Size of the dots on the plot

plt.subplots(1,numberOfDefects, figsize=(12,4)) #Sets the number of subplots

for i in range (0, len(eigenVal)):
    if(count == 0):
        band_edge = float(eigenVal[i][1])
    count = count + 1
    if(eigenVal[i][0] == 'done'):
        i = i + 1
        defect_name = eigenVal[i - count][3] #Gets the name of the defect from file
        defect_name = format_label(defect_name)
        
        plt.subplot(1, numberOfDefects, plotNum)
        plt.tick_params(labelbottom=False,bottom=False, top=False, labeltop=False, labelright=False, labelleft=False, left=False, right=False)
        
        for j in range(1, len(energy) - 1):
            if(occupancy[j] < 0.2): #Plots the unoccupied states
                plt.axhline(energy[j], color = 'black')
                plt.scatter([0.25, 0.75], [energy[j], energy[j]], facecolors='white', edgecolors='black', zorder = 3, s = dotSize)
            elif(occupancy[j] > 0.8): #Plots the occupied states
                plt.axhline(energy[j], color = 'black')
                plt.scatter([0.25, 0.75], [energy[j], energy[j]], color = 'black', zorder = 3, s = dotSize)
            else: #Plots the half-occupied states and splits the levels based on ISPIN = 2 Calculation
                filledState = float(eigenVal[i - (len(energy) - j) - 1][3]) - band_edge
                emptyState = float(eigenVal[i - (len(energy) - j) - 1][4]) - band_edge
                plt.axhline(filledState, color = 'black', xmax = 0.5)
                plt.axhline(emptyState, color = 'black', xmin = 0.5)
                plt.scatter(0.25, filledState, color='black', zorder = 3, s = dotSize)
                plt.scatter(0.75, emptyState, facecolors='white', edgecolors='black', zorder = 3, s = dotSize)
                plt.plot([0.5,0.5], [filledState, emptyState], color = 'black', linestyle = 'dashed')
        
        plt.xlabel(defect_name, fontsize = 12)
        plt.xlim(0,1)
        plt.ylim(0, energy[len(energy) - 1])
        
        energy, occupancy = [], []
        count = 0
        plotNum = plotNum + 1
        
        if(i > len(eigenVal) - 1):
            break
    if(count != 0):
        energy.append(float(eigenVal[i][1]) - band_edge)
        occupancy.append(float(eigenVal[i][2]))
    
del(count, data, f, i, j, defect_name, dotSize, energy, occupancy, emptyState, filledState)
