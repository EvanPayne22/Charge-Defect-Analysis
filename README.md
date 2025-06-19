# Charge Defect Analysis

This repository is designed to aid in the preparation of VASP input files for analyzing charge defects in materials. The ultimate goal is to determine the intrinsic Fermi energy at which the system becomes charge neutral.

To fully utilize this repository, you will need to download the script `sxdefectalign`, written by Christopher Freysoldt. This tool is used to calculate correction terms related to the periodic boundary conditions in VASP simulations. It also accounts for the long-range electrostatic potentials assumed to follow a Gaussian distribution.

Another helpful package is `pydefect`, which provides useful tools for determining the chemical potentials of the constituent elements. However, this step can be skipped as long as your potential file follows the same format as shown below.

## generate_defects.py
### Description

### Input Files

## charge_defect_generator.sh
### Description

### Input Files

## run_sxdefectalign_code.sh
### Description

### Input Files

## make_vatoms_output.sh
### Description

### Input Files

### Sample Plot

## complete_def_en_ef_min.py
### Description

### Input Files

## no_vatoms.py
### Description

### Input Files
