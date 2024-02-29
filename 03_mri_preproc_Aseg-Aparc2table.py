#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 09:56:24 2024

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys
import os
import pandas as pd
import subprocess
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    os.chdir(path_project)
    file = open('subj_List.txt', 'w')
    for item in subj_List:
        file.write(item+"\n")
    file.close()
    subprocess.run(["asegstats2table", "--subjectsfile", "subj_List.txt", "--meas", "volume", "--tablefile", "aseg.txt"])
    subprocess.run(["aparcstats2table", "--subjectsfile", "subj_List.txt", "--hemi", "rh", "--meas", "thickness", "--tablefile", "rh_aparc.txt"])
    subprocess.run(["aparcstats2table", "--subjectsfile", "subj_List.txt", "--hemi", "lh", "--meas", "thickness", "--tablefile", "lh_aparc.txt"])
    df1 = pd.read_csv('aseg.txt', sep='\t')
    df2 = pd.read_csv('rh_aparc.txt', sep='\t')
    df3 = pd.read_csv('lh_aparc.txt', sep='\t')
    df1.to_excel('aseg.xlsx')
    df2.to_excel('rh_aparc.xlsx')
    df3.to_excel('lh_aparc.xlsx')
