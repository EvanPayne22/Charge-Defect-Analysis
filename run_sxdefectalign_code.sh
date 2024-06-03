#!/bin/bash

#Get Directories
directories=$(ls -d */) 

rm ./energies_correction.csv

echo "Defect Name, Bulk Energy, Correction Energy" >> ./energies_correction.csv

for a in $directories
do
	cd $a
	if [ -f "LOCPOT" ]; then 
		#Gets Defect Location by using location specified in POSCAR of the neutral charge state in the header, ex. Rb12 Sb3 I9 0.4159365 0.6027021 0.4107527  
		nonChargeDefect="${a//[0-9\/-]/}"0
		defectLocation=$(head -1 "../$nonChargeDefect/POSCAR" | awk '{print $4 "," $5 "," $6}')
		charge=$(echo "$a" | tr -cd '0-9-')
		# Check if the charge is negative
		if [ "${charge:0:1}" = "-" ]; then
    			# If it's negative, remove the minus sign to make it positive
    			charge="${charge:1}"
		else
    			# If it's positive, add a minus sign to make it negative
    			charge="-$charge"
		fi
		#Runs the sxdefect code: change values/locations as needed, you will also need to have sxdefectalign downloaded
		~/work/CodeFiles/sxdefectalign --ecut 20 --charge $charge --tensor 10.874,10.674,10.263 --center $defectLocation --relative --vdef ~/work/RbSbI/ortho/supercell/"$a"LOCPOT --vref ~/work/RbSbI/ortho/supercell/Bulk/LOCPOT --vasp >> results.txt 
		free_en=$(grep "free  en" OUTCAR | tail -1 | awk '{print $5}')
		results=$(tail -1 "results.txt" | awk '{print $4}')

		echo "$a, $free_en, $results" >> ../energies_correction.csv
		#rm results.txt
	fi
	cd ..
done
