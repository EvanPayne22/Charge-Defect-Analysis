# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:07:04 2024

@author: evanp
"""

"""
Code to plot defect levels across the band gap. Manually enter in the Band Energy and Occupancy from the EIGENVAL file from the VBM to CMB. Follow the formatting as see in eigenVal.txt
If the occupancy is 0.5, write the band energies of each electron after running a spin polarized calculation. Example is given in eigenVal.txt
"""

import matplotlib.pyplot as plt

# Function to format labels with subscript
def format_label(label):
    base, subscript = label.split('_')
    return f"{base}$_{{{subscript}}}$"

data = r"./eigenVal.csv"
# data = r"./eigenVal2.csv"

f = open(data)
eigenVal = f.readlines()

for i in range(0, len(eigenVal)):
    eigenVal[i] = eigenVal[i].split()

numberOfDefects = 9

band = []
occupancy = []

i = 1
k = 1
total = 1

dotSize = 100

plt.subplots(1,numberOfDefects, figsize=(12,4))

while (i < len(eigenVal)):
    title = eigenVal[i][2]
    title = format_label(title)
    while(eigenVal[i]):
        band.append(float(eigenVal[i][0]))
        occupancy.append(float(eigenVal[i][1]))
        total = total + 1
        i = i + 1

    plt.subplot(1,numberOfDefects,k)
    plt.tick_params(labelbottom=False,bottom=False, top=False, labeltop=False, labelright=False, labelleft=False, left=False, right=False)
    vbm = band[0]
    for j in range(1, len(band) - 1):
        band[j] = band[j] - vbm
        if(occupancy[j] < 0.2):
            plt.axhline(band[j], color = 'black')
            plt.scatter([0.25, 0.75], [band[j], band[j]], facecolors='white', edgecolors='black', zorder = 3, s = dotSize)
        elif(occupancy[j] > 0.8):
            plt.axhline(band[j], color = 'black')
            plt.scatter([0.25, 0.75], [band[j], band[j]], color = 'black', zorder = 3, s = dotSize)
        else:
            filledState = float(eigenVal[i - (len(band) - j)][2]) - vbm
            emptyState = float(eigenVal[i - (len(band) - j)][3]) - vbm
            plt.axhline(filledState, color = 'black', xmax = 0.5)
            plt.axhline(emptyState, color = 'black', xmin = 0.5)
            plt.scatter(0.25, filledState, color='black', zorder = 3, s = dotSize)
            plt.scatter(0.75, emptyState, facecolors='white', edgecolors='black', zorder = 3, s = dotSize)
            plt.plot([0.5,0.5], [filledState, emptyState], color = 'black', linestyle = 'dashed')
    
    plt.xlabel(title, fontsize = 12)
    plt.xlim(0,1)
    plt.ylim(0, band[len(band) - 1] - vbm)
    k = k + 1
    
    band = []
    occupancy = []
    
    i = i + 1
    total = total + 1

plt.show()     
