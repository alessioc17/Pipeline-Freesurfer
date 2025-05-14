## REMIND - Regional Extraction and analysis of MRI and PET features for INtegrated Diagnostics

MRI Segmentation Pipeline with Freesurfer and Optional Processing with Petsurfer

Requirements: Python3 (numpy, pandas, mahotas, nibabel, Dcm2niix); Freesurfer; FSL; ANTs; Nipype

* 01: Convert T1 MRI from DICOM to Nifti and then to mgz format
* 02: Execute Freesurfer's ReconAll for structural analysis
* 03: Transform Aparc (cortical VOIs in both hemispheres) and Aseg (sub-cortical VOIs) outputs to a tabular format
* 04: Perform additional GTM segmentation on the T1 MRI
* 05: Convert FDG PET from DICOM to Nifti format
* 06: Spatially normalize FDG PET and GTMSeg to MNI coordinates
* 07: Normalize intensities of the PET and conduct Regional Analysis, resulting in the mean PET uptake in all segmented regions


## Citation

If you use **REMIND** in your research, please cite it as:

Alessio C. (2025). *REMIND: Regional Extraction and analysis of MRI and PET features for Integrated Diagnostics* (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.15410109

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15410109.svg)](https://doi.org/10.5281/zenodo.15410109)
