# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 17:23:00 2024

@author: evanp
"""

import math
import os

poscar = r"./POSCAR"

f = open(poscar)
POSCAR = f.readlines()

def outputFile(tempPOSCAR, addedElement, subbedElement):
    tempString = ""
    
    for n in range (8, len(tempPOSCAR)):
        for o in range(0, len(tempPOSCAR[n])):
            tempString = tempString + str(tempPOSCAR[n][o]) + " "
        tempPOSCAR[n] = tempString
        tempString = ""
    
    vacName = str(addedElement) + "_" + str(subbedElement) + "_0" 
    
    if not os.path.exists(vacName):
        os.mkdir(vacName)
    
    fileLoc = str(vacName) + "\POSCAR"
    
    with open(fileLoc, "w") as file:
        # Loop through the list and write each item to the file
        for item in tempPOSCAR:
            file.write(item + "\n")  # Add a newline character after each item
    
    return tempPOSCAR

def makeVac(lineNumber, poscar, subbedElement):
    
    tempPOSCAR = poscar.copy()
    
    for j in range(0, 8):
        tempPOSCAR[j] = tempPOSCAR[j].strip()
    
    tempPOSCAR[0] = tempPOSCAR[0] + " " + str(poscar[lineNumber][0]) + " " + str(poscar[lineNumber][1]) + " " + str(poscar[lineNumber][2]) 
    del(tempPOSCAR[lineNumber])
    
    numAtoms  = tempPOSCAR[6].split()
    for i in range (len(numAtoms)):
        numAtoms[i] = int(numAtoms[i])
    
    numAtoms[subbedElement] = numAtoms[subbedElement] - 1
    
    numAtomsString = ""
    for m in range(0, len(numAtoms)):
        numAtomsString = numAtomsString + str(numAtoms[m]) + " "
    
    tempPOSCAR[6] = numAtomsString
    
    tempPOSCAR = outputFile(tempPOSCAR, "Va", atomNames[subbedElement])

    return(tempPOSCAR)

def makeSub(lineNumber, poscar, addedElement, subbedElement):
    
    tempPOSCAR = poscar.copy()
        
    for j in range(0, 8):
        tempPOSCAR[j] = tempPOSCAR[j].strip()
        
    tempPOSCAR[0] = tempPOSCAR[0] + " " + str(poscar[lineNumber][0]) + " " + str(poscar[lineNumber][1]) + " " + str(poscar[lineNumber][2]) 
    tempString = tempPOSCAR[lineNumber] 
    del(tempPOSCAR[lineNumber])
    
    numAtoms  = tempPOSCAR[6].split()
    for i in range (len(numAtoms)):
        numAtoms[i] = int(numAtoms[i])
    
    numAtoms[subbedElement] = numAtoms[subbedElement] - 1
    
    start = 9
    for i in range(0, addedElement):
        start = start + numAtoms[i]
        
    tempPOSCAR.insert(start, tempString)
    
    numAtoms[addedElement] = numAtoms[addedElement] + 1
    
    numAtomsString = ""
    for m in range(0, len(numAtoms)):
        numAtomsString = numAtomsString + str(numAtoms[m]) + " "
    
    tempPOSCAR[6] = numAtomsString
    
    tempPOSCAR = outputFile(tempPOSCAR, atomNames[addedElement], atomNames[subbedElement])
    
    return tempPOSCAR
    
def convertToCartesian(poscar):
    latticeConstant = float(poscar[1])
    
    lattice1 = poscar[2].split()
    lattice2 = poscar[3].split()
    lattice3 = poscar[4].split()
    
    latticeX = [float(lattice1[0]), float(lattice2[0]), float(lattice3[0])]
    latticeY = [float(lattice1[1]), float(lattice2[1]), float(lattice3[1])]
    latticeZ = [float(lattice1[2]), float(lattice2[2]), float(lattice3[2])]
    
    x = 0
    y = 0
    z = 0
    
    for i in range (8, len(POSCAR)):
        x = latticeConstant*(latticeX[0]*poscar[i][0] + latticeX[1]*poscar[i][1] + latticeX[2]*poscar[i][2])
        y = latticeConstant*(latticeY[0]*poscar[i][0] + latticeY[1]*poscar[i][1] + latticeY[2]*poscar[i][2])
        z = latticeConstant*(latticeZ[0]*poscar[i][0] + latticeZ[1]*poscar[i][1] + latticeZ[2]*poscar[i][2])
        
        poscar[i] = [x, y, z]
        
    return(poscar)
    

totAtoms = 0
atomNames  = POSCAR[5].split()
numAtoms  = POSCAR[6].split()
for i in range (len(numAtoms)):
    numAtoms[i] = int(numAtoms[i])
    totAtoms = totAtoms + numAtoms[i]

avgx = 0
avgy = 0
avgz = 0

for i in range (8, len(POSCAR)):
    POSCAR[i] = POSCAR[i].split()
    POSCAR[i][0] = float(POSCAR[i][0])
    POSCAR[i][1] = float(POSCAR[i][1])
    POSCAR[i][2] = float(POSCAR[i][2])

if((POSCAR[7].strip()).lower() == "direct"):
    POSCAR = convertToCartesian(POSCAR)
    POSCAR[7] = "Cartesian"

for i in range (8, len(POSCAR)):
    avgx = avgx + float(POSCAR[i][0])
    avgy = avgy + float(POSCAR[i][1])
    avgz = avgz + float(POSCAR[i][2])

avgx = avgx/totAtoms
avgy = avgy/totAtoms
avgz = avgz/totAtoms

start = 8
for i in range(0, len(numAtoms)):
    deviation = []
    for j in range (0, numAtoms[i]):
        deviation.append(math.sqrt((POSCAR[j + start][0] - avgx)**2 + (POSCAR[j + start][1] - avgy)**2 + (POSCAR[j + start][2] - avgz)**2))
    centralLoc = deviation.index(min(deviation))
    print(centralLoc + 1)
    print(POSCAR[start + centralLoc])
    
    vacancy = makeVac(centralLoc + start, POSCAR, i)
    for k in range (0, len(numAtoms)):
        if(i != k):
            makeSub(centralLoc + start, POSCAR, k, i)
    
    start = start + numAtoms[i]
