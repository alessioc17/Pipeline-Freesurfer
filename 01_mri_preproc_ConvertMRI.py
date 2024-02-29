# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 12:32:57 2024

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys
import os
from nipype.interfaces.dcm2nii import Dcm2niix
from nipype.interfaces.freesurfer import MRIConvert
from multiprocessing import cpu_count
from joblib import Parallel, delayed
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

def ciclo_convertMRI(subj_id, path_data):
    dir_T1_dicom = path_data + subj_id + '/mri/orig/'
    if os.path.exists(dir_T1_dicom):
        # dicom -> nifti
        converter = Dcm2niix()
        converter.inputs.source_dir = dir_T1_dicom
        converter.inputs.output_dir = dir_T1_dicom
        converter.inputs.out_filename = '001'
        converter.inputs.bids_format = False
        converter.inputs.compress = 'n'
        converter.inputs.philips_float = True
        converter.run()
        # nifti -> mgz
        mriconv = MRIConvert()
        mriconv.inputs.in_file = dir_T1_dicom + '001.nii'
        mriconv.inputs.out_file = dir_T1_dicom + '001.mgz'
        mriconv.inputs.out_type = 'mgz'
        mriconv.run()
        print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
        f = open(path_project + 'logSubjects_convertMRI.txt', 'a')
        f.write("ConvertMRI complete for subject " + subj_id + "\n")
        f.close()
    else:
        print("Unable to run ConvertMRI. T1 is missing in: " + subj_id)
        f2 = open(path_project + 'logSubjects_convertMRI_warning.txt', 'a')
        f2.write("Unable to run ConvertMRI. T1 is missing in: " + subj_id + "\n")
        f2.close()

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    ris = Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_convertMRI)(subj_id, path_data) for subj_id in subj_List)
