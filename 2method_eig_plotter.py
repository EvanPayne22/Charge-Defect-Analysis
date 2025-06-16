# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 00:52:18 2025

@author: aheib
"""

import matplotlib.pyplot as plt
import argparse
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import MultipleLocator

parser = argparse.ArgumentParser(description="Arguments for charge defect ",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-hseext", nargs='?', type=bool, default = False, help="shows HSE region on PBE or alt plots")
parser.add_argument("-fileloc", nargs='?', default = "./eigenVal.txt", help="sets the location of the file")
parser.add_argument("-saveloc", nargs='?', default = "./pbehseeigplot.png", help="sets the location of the file")
parser.add_argument("-linewidth", nargs='?', type=int, default = 2, help="sets line thickness")
parser.add_argument("-dotsize", nargs='?', type=int, default = 100, help="sets size of the dotd on plots")
parser.add_argument("-fontsize", nargs='?', type=int, default = 18, help="sets fontsize")
parser.add_argument("-plotwidth", nargs='?', type=int, default = 6, help="sets width of the plots (I recommend 6 per plot)")
args = parser.parse_args()
config = vars(args)

#Function to format defect names with subscript
def format_label(label):
    base, subscript = label.split('_')
    return f"{base}$_{{{subscript}}}$"

data = config["fileloc"]

f = open(data)
eigenVal = f.readlines()

numberOfDefects = 0 #The number of defects being plotted

for i in range (0, len(eigenVal)):
    if (eigenVal[i][0] == 'd'): #Countes the Number of Defects Being Plotted
        numberOfDefects += 1
    eigenVal[i] = eigenVal[i].split()

numberOfDefects = int(numberOfDefects/2)  
    
count = 0 #Counter for reading eigenVal file
plotNum = 0 #Counter to store which sub plot data is stored for
defectCount = 0#Counts the number of defects gone through

energy = [] #Energy Level of the Defect in energy Gap
occupancy = [] #Occupancy of Defect States
dotSize = config["dotsize"] #Size of the dots on the plot
fontSize = config["fontsize"] #Default value for font size
lineWidth = config["linewidth"] #Sets the thickness of the lines

plt.subplots(1,numberOfDefects, figsize=(config["plotwidth"],4)) #Sets the number of subplots

for i in range (0, len(eigenVal)):
    if(count == 0):
        band_edge = float(eigenVal[i][1])
    count = count + 1
    
    #Reads All Energies and Occupancies for Nuetral Defect
    if(eigenVal[i][0] == 'done'):
        if(defectCount%2 == 0):
            pbe_defect = True #Bool to confirm if current defect is PBE or HSE
            position1 = 0.1875 #Position of electron 1 in plot
            position2 = 0.3125 #Position of electron 2 in plot
            halfpt = 0.25 #Position of dashed line for half filled states
            hormin = 0.125 #Minimum for horisontal lines
            hormax = 0.375 #Maximum for horisontal lines
            plotNum = plotNum + 1
            plt.subplot(1, numberOfDefects, plotNum)
        else:
            pbe_defect = False #Bool to confirm if current defect is PBE or HSE
            position1 = 0.6875 #Position of electron 1 in plot
            position2 = 0.8125 #Position of electron 2 in plot
            halfpt = 0.75 #Position of dashed line for half filled states
            hormin = 0.625 #Minimum for horisontal lines
            hormax = 0.875 #Maximum for horisontal lines
            
            ax = plt.gca()  # Get current subplot (Axes) instance

            #Adds PBE and HSE labels
            ax.text(0.2, -0.03, "PBE", transform=ax.transAxes,
                    ha='left', va='top', fontsize=fontSize)
            ax.text(0.9, -0.03, "HSE-SOC", transform=ax.transAxes,
                    ha='right', va='top', fontsize=fontSize)
            ax.text(0.55, 0.5, defect_name, transform=ax.transAxes,
                    ha='right', va='top', fontsize=fontSize)
            #Formats the y-axis
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.tick_params(axis='y', labelsize=fontSize)  # Change 10 to your desired font size
            ax.yaxis.set_minor_locator(MultipleLocator(0.25))
            ax.tick_params(axis='y', which='minor', length=4, width=1, labelsize=0, label1On=False)


        
        defectCount += 1
        
        #Sets read range based on input file
        if(pbe_defect):
           jmin = 2
           jmax = len(energy) - 2
        else:
            jmin = 1
            jmax = len(energy) - 1
        
        i = i + 1
        defect_name = eigenVal[i - count][3] #Gets the name of the defect from file
        defect_name = format_label(defect_name) #Forats the defect name for plot
        
        plt.tick_params(labelbottom=False,bottom=False, top=False, labeltop=False, labelright=False, labelleft=True, left=True, right=False)
        
        for j in range(jmin, jmax):
            if(occupancy[j] < 0.2): #Plots the unoccupied states
                plt.axhline(energy[j], color = 'black', xmax = hormax, xmin = hormin, lw = lineWidth)
                plt.scatter([position1, position2], [energy[j], energy[j]], facecolors='white', edgecolors='black', zorder = 3, s = dotSize)
            elif(occupancy[j] > 0.8): #Plots the occupied states
                plt.axhline(energy[j], color = 'black', xmax = hormax, xmin = hormin, lw = lineWidth)
                plt.scatter([position1, position2], [energy[j], energy[j]], color = 'black', zorder = 3, s = dotSize)
            else: #Plots the half-occupied states and splits the levels based on ISPIN = 2 Calculation
                filledState = float(eigenVal[i - (len(energy) - j) - 1][3]) - band_edge
                emptyState = float(eigenVal[i - (len(energy) - j) - 1][4]) - band_edge
                plt.axhline(filledState, color = 'black', xmax = halfpt, xmin = hormin, lw = lineWidth)
                plt.axhline(emptyState, color = 'black', xmin = halfpt, xmax = hormax, lw = lineWidth)
                plt.scatter(position1, filledState, color='black', zorder = 3, s = dotSize)
                plt.scatter(position2, emptyState, facecolors='white', edgecolors='black', zorder = 3, s = dotSize)
                plt.plot([halfpt,halfpt], [filledState, emptyState], color = 'black', linestyle = 'dashed', lw = lineWidth)
        
        cond_band_edge = energy[len(energy) - 1] #Conduction Band Edge
        
        if(pbe_defect):
            cond_band_edge_pbe = energy[len(energy) - 2] #CBM for PBE
            val_band_edge_pbe = energy[1] #VBM for PBE
            plt.fill([0,0,0.5,0.5], [0, val_band_edge_pbe, val_band_edge_pbe, 0], color = 'grey')
            plt.fill([0,0,0.5,0.5], [cond_band_edge_pbe, cond_band_edge, cond_band_edge, cond_band_edge_pbe], color = 'grey')
        
        plt.xlim(0,1)
        plt.ylim(0, cond_band_edge)
        plt.ylabel("Energy (eV)", fontsize = fontSize)
        
        energy, occupancy = [], []
        count = 0
        
        if(i > len(eigenVal) - 1):
            break
    if(count != 0):
        energy.append(float(eigenVal[i][1]) - band_edge)
        occupancy.append(float(eigenVal[i][2]))

plt.savefig(config["saveloc"])
plt.show()

del(count, data, f, i, j, jmin, jmax, defect_name, dotSize, energy, occupancy, emptyState, filledState,
    args, ax, band_edge, cond_band_edge, cond_band_edge_pbe, config, defectCount, eigenVal, plotNum, fontSize,
    halfpt, hormax, hormin, lineWidth, parser, pbe_defect, position1, position2, val_band_edge_pbe)
