#!/bin/bash

#Enter in defect name
defectName="Rb_i1"
directoryName="$defectName"_0
#Gets the number of electrons in nuetral charge state 
electrons=$(grep NELECT $directoryName/OUTCAR | awk '{printf "%0.f\n", $3}')

#Write needed charge states
for a in {1..2} -1 -2
do
	newName="$defectName"_"$a"
	mkdir $newName
	cp $directoryName/CONTCAR $newName/POSCAR
	cp job.vasp6 INCAR POTCAR KPOINTS $newName
	cd $newName
	#Generates number of electrons for charge defect
	newCharge=$(($electrons - $a))
	echo "NELECT = $newCharge" >> INCAR
	#qsub job.vasp6
	cd ..
done
