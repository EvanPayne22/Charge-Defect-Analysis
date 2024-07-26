#!/bin/bash

#Input: Directory with neutral charge state defect
#Output: Directories of specified run states with desired NELECT in INCAR

#Enter in defect name
defectName="Rb_i1"
directoryName="$defectName"_0
#Gets the number of electrons in nuetral charge state 
electrons=$(grep NELECT $directoryName/OUTCAR | awk '{printf "%0.f\n", $3}')

#Write needed charge states (do not include 0 since that charge state is already generated)
for a in {1..2} {-2..-1}
do
	newName="$defectName"_"$a"
	mkdir $newName
	cp $directoryName/CONTCAR $newName/POSCAR
 	#job.vasp6 is a run file so edit that to match your submission script
	cp $directoryName/job.vasp6 $directoryName/INCAR $directoryName/POTCAR $directoryName/KPOINTS $newName
	cd $newName
	#Generates number of electrons for charge defect
	newCharge=$(($electrons - $a))
	echo "NELECT = $newCharge" >> INCAR
	#Add the correct script to run vasp
 	#qsub job.vasp6
	cd ..
done
