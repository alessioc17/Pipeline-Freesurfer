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
os.environ["OMP_NUM_THREADS"] = "1"  # Limita i thread OpenMP globalmente a 1
os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = "1"  # per FreeSurfer

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
        
        print(f"\n########### Subject {subj_id} complete ###########\n")
        with open(path_project + 'logSubjects_reconAll.txt', 'a') as f1:
            f1.write(f"ReconAll complete for subject {subj_id}\n")
    else:
        print(f"Unable to run ReconAll. T1 is missing in: {subj_id}")
        with open(path_project + 'logSubjects_reconAll_warning.txt', 'a') as f2:
            f2.write(f"Unable to run ReconAll. T1 is missing in: {subj_id}\n")

def check_failed_subjects(subj_List, path_data):
    failed_subjects = []
    for subj_id in subj_List:
        status_file = os.path.join(path_data, subj_id, 'scripts', 'recon-all-status.log')
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                last_line = f.readlines()[-1].strip()
                if not last_line.startswith(f"recon-all -s {subj_id} finished without error"):
                    failed_subjects.append(subj_id)
        else:
            failed_subjects.append(subj_id)
    return failed_subjects

def process_in_batches(subj_List, path_data, batch_size=24):
    total_subjects = len(subj_List)
    for i in range(0, total_subjects, batch_size):
        batch = subj_List[i:i+batch_size]
        Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_reconAll)(subj_id, path_data) for subj_id in batch)
        print(f"Batch {i//batch_size + 1} completed")

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/workspaces/testpippo/Data/HBD/harmonized_with_stargan_to_Gyroscan/star_Guys_harm_temp/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    
    start_time = time.time()
    process_in_batches(subj_List, path_data)
    
    first_failed = check_failed_subjects(subj_List, path_data)
    if first_failed:
        with open(path_project + 'logSubjects_failed_once.txt', 'w') as f:
            f.write("\n".join(first_failed) + "\n")
        print(f"Retrying {len(first_failed)} subjects that failed the first time...")
        process_in_batches(first_failed, path_data)
        second_failed = check_failed_subjects(first_failed, path_data)
        if second_failed:
            with open(path_project + 'logSubjects_failed_twice.txt', 'w') as f:
                f.write("\n".join(second_failed) + "\n")
            print(f"Warning: {len(second_failed)} subjects failed twice. Check logSubjects_failed_twice.txt")
    
    print(f"--- {time.time() - start_time} seconds (for recon-all) ---")
