#!/bin/bash
  
#Get Directories
directories=$(ls -d */)

rm ./energies_correction.csv

echo "Defect Name, Bulk Energy, Correction Energy" >> ./energies_correction.csv

bulk="../latticeRelax/"
free_en=$(grep TOTEN "$bulk"OUTCAR | tail -1 | awk '{printf $5}')

echo "bulk, $free_en, 0" >> ./energies_correction.csv


for a in $directories
do
        cd $a
        if [ -f "LOCPOT" ]; then
                #Gets Defect Location by using location specified in POSCAR header, ex. Supercell of Rb12 I_Sb at 0.4159365 0.6027021   0.4107527  
                string=${a: -3}
                nonChargeDefect="${a: 0 : -3}""${string//[0-9\/-]/}"0
                defectLocation=$(head -1 "../$nonChargeDefect/POSCAR" | awk '{print $3 "," $4 "," $5}')
                charge=$(echo "$string" | tr -cd '0-9-')
                # Check if the charge is negative
                if [ "${charge:0:1}" = "-" ]; then
                        # If it's negative, remove the minus sign to make it positive
                        charge="${charge:1}"
                else
                        # If it's positive, add a minus sign to make it negative
                        charge="-$charge"
                fi
                echo $charge
                #Runs the sxdefect code: change values/locations as needed
                ~/work/bin/sxdefectalign --ecut 30 --charge $charge --tensor 11.04,11.04,11.04  --center $defectLocation --relative --vdef ./LOCPOT --vref ../"$bulk"LOCPOT --vasp >> results.txt
                free_en=$(grep "free  en" OUTCAR | tail -1 | awk '{print $5}')
                results=$(tail -1 "results.txt" | awk '{print $4}')

                echo "$a, $free_en, $results" >> ../energies_correction.csv
                #rm results.txt
        fi
        cd ..
done
