# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:17:57 2023

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

# matplotlib qt5
import sys, os, mahotas
import numpy as np
import nibabel as nib
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/mnt/d/Dati_AMYITA/AD_Atipici_Cecchin/'
    path_data = path_project + 'data_finale/'
    subj_List = sorted(os.listdir(path_data))
    df_VOI = pd.read_excel('/mnt/c/Users/Utente/OneDrive - IRCCS Ospedale Policlinico San Martino/San Martino Ricercatore sanitario LIS-COMP/Progetti/MappingRegions/VOI_list.xlsx', sheet_name="VOI_list", usecols=[0,1,2,3,4,5,6,7,8,9])
    df_norm_wm_VOI_mean_subj, df_norm_wm_VOI_std_subj, df_norm_wm_VOI_size_subj = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    SUV_wb, SUV_cb, SUV_wm, SUVR_wb_on_cb, SUVR_wb_on_wm = [], [], [], [], []
    
    for subj_id in subj_List:
        if subj_id[0] != '.' and subj_id != 'fsaverage':
            # Caricare la segmentazione
            SEG = path_data + subj_id + '/mri/aparc+aseg_on_mni.nii.gz'
            if os.path.exists(SEG):
                SEG_im = nib.load(SEG)
                SEG_array = nib.load(SEG).get_fdata(dtype="float32")
                SEG_array_32VOI = np.copy(SEG_array)
                for l in range(len(df_VOI['area_index_gtmseg'])):
                    SEG_array_32VOI[SEG_array == df_VOI['area_index_gtmseg'][l]] = df_VOI['area_index_32VOI'][l]               
                nib.save(nib.Nifti1Image(SEG_array_32VOI, SEG_im.affine), path_data + subj_id + '/mri/aparc+aseg_on_mni_32VOI.nii.gz')
                
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
                    SEG_array_32VOI_crop = SEG_array_32VOI[left : left + PET_shape[0], bottom : bottom + PET_shape[1], inferior : inferior + PET_shape[2]]

                    # Isolare le VOI per la normalizzazione di intensità ed eventualmente contrarle per ridurre gli effetti di bordo dovuti alla registrazione
                    #wb_VOI = np.isin(SEG_array_crop, [3008,3009,3010,3011,3012,3013,3014,3015,3016,3017,3018,3019,3020])
                    wb_VOI = np.isin(SEG_array_crop, [1001,1002,1003,1005,1006,1007,1008,1009,1010,1011,1012,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,1023,1024,1025,1026,1027,1028,1029,1030,1031,1032,1033,1034,1035,2001,2002,2003,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035])
                    cb = np.isin(SEG_array_crop, [7, 8, 46, 47]) # cervelletto (materia bianca (7,46) e corteccia (8,47))
                    cb_perim = mahotas.bwperim(cb)
                    cb_VOI = np.bitwise_xor(cb, cb_perim)
                    wm = np.isin(SEG_array_crop, [2, 41]) # white matter destra e sinistra
                    wm_perim = mahotas.bwperim(wm)
                    wm_VOI = np.bitwise_xor(wm, wm_perim)   # plt.imshow(wm_VOI[:,:,150])
                    
                    # Trasferire le VOI sulla PET e calcolare la media dei conteggi in tali VOI
                    SUV_wb.append(np.mean(PET_array[wb_VOI]))
                    SUV_cb.append(np.mean(PET_array[cb_VOI]))
                    SUV_wm.append(np.mean(PET_array[wm_VOI]))
                    SUVR_wb_on_cb.append(np.mean(PET_array[wb_VOI])/np.mean(PET_array[cb_VOI]))
                    SUVR_wb_on_wm.append(np.mean(PET_array[wb_VOI])/np.mean(PET_array[wm_VOI]))
                    
                    # Dividere i conteggi della PET per il valore medio di uptake nella VOI di riferimento (SUVR)
                    PET_norm_wb = PET_array/SUV_wb[-1]
                    PET_norm_wm = PET_array/SUV_wm[-1]
                    PET_norm_cb = PET_array/SUV_cb[-1]
                    #nib.save(nib.Nifti1Image(PET_norm_cb, affine=PET_im.affine), path_pet + 'FDGPETonMNI_norm_cb.nii.gz')
                    
                    # Analisi regionale
                    VOI_list = list(np.unique(SEG_array_32VOI_crop).astype(int))
                    VOI_list = [j for j in VOI_list if j not in {0,2,4,5,7,8,14,15,16,24,28,29,30,31,41,43,44,46,47,60,62,63,72,77,80,85,251,252,253,254,255,}]
                    PET_norm_wm_VOI_i_mean, PET_norm_wm_VOI_i_std, PET_norm_wm_VOI_i_size = [], [], []
                    for i in VOI_list:
                        VOI_i = np.isin(SEG_array_32VOI_crop, [i])
                        PET_norm_wm_VOI_i = PET_norm_wm[VOI_i]
                        PET_norm_wm_VOI_i_mean.append(np.mean(PET_norm_wm_VOI_i))
                        PET_norm_wm_VOI_i_std.append(np.std(PET_norm_wm_VOI_i))
                        PET_norm_wm_VOI_i_size.append(np.count_nonzero(PET_norm_wm_VOI_i))
                    header = pd.MultiIndex.from_product([[subj_id]])
                    df_norm_wm_VOI_mean = (pd.DataFrame(PET_norm_wm_VOI_i_mean, index=VOI_list, columns=header)).round(3)
                    df_norm_wm_VOI_mean_subj = pd.concat([df_norm_wm_VOI_mean_subj, df_norm_wm_VOI_mean], axis=1)
                    df_norm_wm_VOI_std = (pd.DataFrame(PET_norm_wm_VOI_i_std, index=VOI_list, columns=header)).round(3)
                    df_norm_wm_VOI_std_subj = pd.concat([df_norm_wm_VOI_std_subj, df_norm_wm_VOI_std], axis=1)
                    df_norm_wm_VOI_size = (pd.DataFrame(PET_norm_wm_VOI_i_size, index=VOI_list, columns=header)).round(3)
                    df_norm_wm_VOI_size_subj = pd.concat([df_norm_wm_VOI_size_subj, df_norm_wm_VOI_size], axis=1)
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
    with pd.ExcelWriter(path_project + 'tabella_AMYITA_amy_32VOI_wm.xlsx') as writer:  
        df_norm_wm_VOI_mean_subj.transpose().to_excel(writer, sheet_name='Mean')
        df_norm_wm_VOI_std_subj.transpose().to_excel(writer, sheet_name='Std')
        df_norm_wm_VOI_size_subj.transpose().to_excel(writer, sheet_name='Sample_Size')
