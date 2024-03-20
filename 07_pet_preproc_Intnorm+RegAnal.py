# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:17:57 2023

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

# matplotlib qt5
import sys
import os
import numpy as np
import nibabel as nib
import mahotas
import pandas as pd
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1'

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/mnt/d/Dati_AMYITA/'
    path_data = path_project + 'data 19-12-2023/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    df_norm_wb_VOI_subj = pd.DataFrame()
    SUVR_wb_on_cb, SUVR_wb_on_wm = [], []
    
    for subj_id in subj_List:
        if subj_id[0] != '.' and subj_id != 'fsaverage':
            
            # Caricare la segmentazione
            SEG = path_data + subj_id + '/mri/gtmseg_on_mni.nii.gz'
            if os.path.exists(SEG):
                SEG_im = nib.load(SEG)
                SEG_array = nib.load(SEG).get_fdata(dtype="float32")
                
                # Caricare la PET registrata su spazio MNI
                path_pet = path_data + subj_id + '/amypet/norm/'
                pet = path_pet + 'PETonMNI.nii.gz'
                if os.path.exists(pet):
                    PET_im = nib.load(pet)
                    PET_array = nib.load(pet).get_fdata(dtype="float32")
                    PET_shape = PET_array.shape
                    
                    # Croppare la segmentazione in modo da allinearla con la PET (esse condividono già il centro RAS)
                    PET_orig = [round(PET_im.affine[0][3], 2), round(PET_im.affine[1][3], 2), round(PET_im.affine[2][3], 2)]
                    SEG_orig = [round(SEG_im.affine[0][3], 2), round(SEG_im.affine[1][3], 2), round(SEG_im.affine[2][3], 2)]
                    left = round(abs(SEG_orig[0] - PET_orig[0]))
                    bottom = round(abs(SEG_orig[1] - PET_orig[1]))
                    inferior = round(abs(SEG_orig[2] - PET_orig[2]))
                    SEG_array_crop = SEG_array[left : left + PET_shape[0], bottom : bottom + PET_shape[1], inferior : inferior + PET_shape[2]]

                    # Isolare le VOI per la normalizzazione di intensità ed eventualmente contrarle per ridurre gli effetti di bordo dovuti alla registrazione
                    wb_VOI = np.isin(SEG_array_crop, [1001,1002,1003,1005,1006,1007,1008,1009,1010,1011,1012,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,2001,2002,2003,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035])
                    cb = np.isin(SEG_array_crop, [7, 8, 46, 47]) # cervelletto (materia bianca (7,46) e corteccia (8,47))
                    cb_perim = mahotas.bwperim(cb)
                    cb_VOI = np.bitwise_xor(cb, cb_perim)
                    wm = np.isin(SEG_array_crop, [2, 41]) # white matter destra e sinistra
                    wm_perim = mahotas.bwperim(wm)
                    wm_VOI = np.bitwise_xor(wm, wm_perim)   # plt.imshow(wm_VOI[:,:,150])
                    
                    # Trasferire le VOI sulla PET e calcolare la media dei conteggi in tali VOI
                    SUV_wb = np.mean(PET_array[wb_VOI])
                    SUV_cb = np.mean(PET_array[cb_VOI])
                    SUV_wm = np.mean(PET_array[wm_VOI])
                    SUVR_wb_on_cb.append(SUV_wb/SUV_cb)
                    SUVR_wb_on_wm.append(SUV_wb/SUV_wm)
                    
                    # Dividere i conteggi della PET per il valore medio di uptake nella VOI di riferimento (SUVR)
                    PET_norm_wb = PET_array/SUV_wb
                    nib.save(nib.Nifti1Image(PET_norm_wb, affine=PET_im.affine), path_pet + 'PETonMNI_norm_wb.nii.gz')
                    
                    # Analisi regionale
                    VOI_list = list(np.unique(SEG_array_crop).astype(int))
                    VOI_list = [j for j in VOI_list if j not in {0, 130, 258, 165, 257}]
                    PET_norm_wb_VOI_i_mean = []
                    for i in VOI_list:
                        VOI_i = np.isin(SEG_array_crop, [i])
                        PET_norm_wb_VOI_i = PET_norm_wb[VOI_i]
                        PET_norm_wb_VOI_i_mean.append(np.mean(PET_norm_wb_VOI_i))
                    header = pd.MultiIndex.from_product([[subj_id]])
                    df_norm_wb_VOI = (pd.DataFrame(PET_norm_wb_VOI_i_mean, index=VOI_list, columns=header)).round(3)
                    df_norm_wb_VOI_subj = pd.concat([df_norm_wb_VOI_subj, df_norm_wb_VOI], axis=1)
                    print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
                    f1 = open(path_project + 'logSubjects.txt', 'a')
                    f1.write("Run complete for subject " + subj_id + "\n")
                    f1.close()
                else:
                    print("PET is missing in Subject", subj_id)
                    f2 = open(path_project + 'logSubjects_warning.txt', 'a')
                    f2.write("PET is missing in Subject " + subj_id + "\n")
                    f2.close()
            else:
                print("Segmentation is missing in Subject", subj_id)
                f2 = open(path_project + 'logSubjects_warning.txt', 'a')
                f2.write("Segmentation is missing in Subject " + subj_id + "\n")
                f2.close()   
    df_VOI = df_norm_wb_VOI_subj.transpose()
    df_VOI.to_excel(path_project + 'tabella_VOI_amy_new.xlsx')