directories=$(ls -d */)

rm -f ./vAtoms_output.csv 

echo "Column 1, Column 2, Column 3, Column 4, Column 5" >> ./vAtoms_output.csv

for a in $directories
do
	cd $a
	if [ -e "./vAtoms.dat" ]
	then
		echo "stop,$a" >> ../Atoms_output.csv
		awk '{print $1 "," $2 "," $3 "," $4 "," $5}' vAtoms.dat >> ../vAtoms_output.csv
	fi
	cd ..
done

echo " " >> ./vAtoms_output.csv
echo "stop" >> ./vAtoms_output.csv


