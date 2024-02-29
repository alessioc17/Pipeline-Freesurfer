#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 14:42:00 2024

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys
import os
from nipype.interfaces.freesurfer import petsurfer
import time
from multiprocessing import cpu_count
from joblib import Parallel, delayed
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

def ciclo_gtmseg(subj_id, path_data):
    if subj_id[0] != '.' and subj_id != 'fsaverage':
        check_reconall = path_data + subj_id + '/mri/aseg.mgz'
        if os.path.exists(check_reconall):
            gtmseg = petsurfer.GTMSeg()
            gtmseg.inputs.subject_id = subj_id
            gtmseg.run()
            print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
            f1 = open(path_project + 'logSubjects_gtmseg.txt', 'a')
            f1.write("GTMSeg complete for subject " + subj_id + "\n")
            f1.close()
        else:
            print("Unable to run GTMSeg. ReconAll is missing in Subject", subj_id)
            f2 = open(path_project + 'logSubjects_gtmseg_warning.txt', 'a')
            f2.write("Unable to run GTMSeg. ReconAll is missing in Subject " + subj_id + "\n")
            f2.close()
            
if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    start_time = time.time()
    ris = Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_gtmseg)(subj_id, path_data) for subj_id in subj_List)
    print("--- %s seconds (for gtmseg) ---" % (time.time() - start_time))
