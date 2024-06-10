Generate the energies_correction.csv file using files from VASP with correction values obtained using sxdefectalign written by Christoph Freysoldt. The correction values can also be obtained using other methods but the code requires the exact formatting shown in the energies_correction.csv.

The run_sxdefectalign_code.sh has a lot of formatting involved. A few things that will need to be changed are the paths to your bulk cell and defect cell. The dielectric constant for your material will also have to be entered. The last thing which is mentioned earlier in the file is
that the defect location is placed at the top of my POSCAR. The columns that the script reads may need adjusted depending on how long your first line is in the POSCAR. It is also important to note that I put the original location at the top of the POSCAR using a script and that is not a default feature.

I've also attached my generate_defects.py script that will generate vacancies and substitution defects. It also places the original defects coordinates at the top of the file for the sxdefect script talked about above.

The energies_correction.csv can be generated by using the bash script labeled run_sxdefectalign_code.sh. The script will require the dielectric tensor, the location of the defect, and a correctly formatted file system.
An example of the file system is also attached.
The location of the defects was written at the top of the POSCAR to be used for this script.

Use the vAtoms_code.py to generate a file with separated charges and the delta-V correction energies. 
The delta V correction energies are the corrections that are needed to account for VASP needing to start at 0 eV for each run.

The energies_final.csv generated in vAtoms_code.py can be used in both the def_en_ef_all.py and def_en_ef_min.py.
The def_en_ef_all.py will plot all individual charge states of a defect over a range of Fermi energies.
The def_en_ef_min.py will plot the lowest energy charge defects individually and in a complete plot with all of the other defects.
Notes: As long as the energies_final.csv looks the same as the given example then it does not need to be run through vAtoms_code.py.

The complete_def_en_ef_min.py combines the vAtoms_code.py to the def_en_ef_min.py. It also adds a feature which can be ignored if using the two individual scripts. The "complete" code will take in a .yaml file generated using pydefect to use for the chemical potentials. 
In my script, you will need to add the reservoir energies from the bulk cells of the elements in your material. And just below that make sure to enter in the names of the elements in the same order as your vAtoms_output.csv.

All of the plots are also located in the repository as examples to see exactly what I am talking about.
