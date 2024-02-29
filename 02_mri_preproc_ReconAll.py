#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 12:17:09 2024

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys
import os
from nipype.interfaces.freesurfer import ReconAll
import time
from multiprocessing import cpu_count
from joblib import Parallel, delayed
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

def ciclo_reconAll(subj_id, path_data):
    try:
        os.remove(path_data + subj_id + '/scripts/IsRunning.lh+rh')
        os.remove(path_data + subj_id + '/scripts/IsRunning.lh')
        os.remove(path_data + subj_id + '/scripts/IsRunning.rh')
    except:
        pass
    T1_mgz = path_data + subj_id + '/mri/orig/001.mgz'
    if os.path.exists(T1_mgz):
        reconall = ReconAll()
        reconall.inputs.directive = 'all'
        reconall.inputs.subjects_dir = path_data
        reconall.inputs.subject_id = subj_id
        reconall.inputs.T1_files = T1_mgz
        reconall.inputs.parallel = True
        reconall.run()
        print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
        f1 = open(path_project + 'logSubjects_reconAll.txt', 'a')
        f1.write("ReconAll complete for subject " + subj_id + "\n")
        f1.close()
    else:
        print("Unable to run ReconAll. T1 is missing in: " + subj_id)
        f2 = open(path_project + 'logSubjects_reconAll_warning.txt', 'a')
        f2.write("Unable to run ReconAll. T1 is missing in: " + subj_id + "\n")
        f2.close()
    
if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    start_time = time.time()
    ris = Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_reconAll)(subj_id, path_data) for subj_id in subj_List)
    print("--- %s seconds (for reconaAll) ---" % (time.time() - start_time))
