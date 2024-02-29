# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 14:44:17 2023

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys
import os
from nipype.interfaces.dcm2nii import Dcm2niix
from multiprocessing import cpu_count
from joblib import Parallel, delayed
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

def ciclo_convertFDG(subj_id, path_data):
    if subj_id[0] != '.' and subj_id != 'fsaverage':
        dir_FDG_dicom = path_data + subj_id + '/fdgpet/'
        if os.path.exists(dir_FDG_dicom):
            # dicom -> nifti
            converter = Dcm2niix()
            converter.inputs.source_dir = dir_FDG_dicom
            converter.inputs.output_dir = dir_FDG_dicom
            converter.inputs.out_filename = 'fdg'
            converter.inputs.bids_format = False
            converter.inputs.compress = 'n'
            converter.inputs.philips_float = True
            converter.run()
            print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
            f = open(path_project + 'logSubjects_convertFDG.txt', 'a')
            f.write("ConvertFDG complete for subject " + subj_id + "\n")
            f.close()
        else:
            print("Unable to run ConvertFDG. FDG-PET is missing in: " + subj_id)
            f2 = open(path_project + 'logSubjects_convertFDG_warning.txt', 'a')
            f2.write("Unable to run ConvertFDG. FDG-PET is missing in: " + subj_id + "\n")
            f2.close()

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    ris = Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_convertFDG)(subj_id, path_data) for subj_id in subj_List)
