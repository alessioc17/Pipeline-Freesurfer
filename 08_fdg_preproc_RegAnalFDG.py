# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:17:57 2023

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys
import os
import numpy as np
import nibabel as nib
import pandas as pd
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    df_VOI_fdg_subj_wbmean,df_VOI_fdg_subj_wbstd,df_VOI_fdg_subj_ponsmean,df_VOI_fdg_subj_ponsstd = (pd.DataFrame() for i in range(4))
    for subj_id in subj_List:
        if subj_id[0] != '.' and subj_id != 'fsaverage':
            
            # Caricare segmentazione e PET FDG
            SEG = path_data + subj_id + '/mri/gtmseg_on_mni.nii.gz'
            if os.path.exists(SEG):
                SEG_im = nib.load(SEG)
                SEG_array = nib.load(SEG).get_fdata(dtype="float32")   
                FDGPETonMNI_intnorm_wb = path_data + subj_id + '/fdgpet/norm/FDGPETonMNI_intnorm_wb.nii.gz'
                FDGPETonMNI_intnorm_pons = path_data + subj_id + '/fdgpet/norm/FDGPETonMNI_intnorm_pons.nii.gz'
                if os.path.exists(FDGPETonMNI_intnorm_wb):
                    FDGPET_wb_im = nib.load(FDGPETonMNI_intnorm_wb)
                    FDGPET_wb_array = nib.load(FDGPETonMNI_intnorm_wb).get_fdata(dtype="float32")
                    FDGPET_wb_shape = FDGPET_wb_array.shape
                    FDGPET_pons_array = nib.load(FDGPETonMNI_intnorm_pons).get_fdata(dtype="float32")
                    
                    # Croppare la segmetazione in modo da allinearla con la PET FDG (esse condividono già il centro RAS)
                    FDGPET_wb_orig = [round(FDGPET_wb_im.affine[0][3], 2), round(FDGPET_wb_im.affine[1][3], 2), round(FDGPET_wb_im.affine[2][3], 2)]
                    SEG_orig = [round(SEG_im.affine[0][3], 2), round(SEG_im.affine[1][3], 2), round(SEG_im.affine[2][3], 2)]
                    left = round(abs(SEG_orig[0] - FDGPET_wb_orig[0]))
                    bottom = round(abs(SEG_orig[1] - FDGPET_wb_orig[1]))
                    inferior = round(abs(SEG_orig[2] - FDGPET_wb_orig[2]))
                    SEG_array_cropped = SEG_array[left : left + FDGPET_wb_shape[0], bottom : bottom + FDGPET_wb_shape[1], inferior : inferior + FDGPET_wb_shape[2]]
                    VOI_list = list(np.unique(SEG_array_cropped).astype(int))
                    VOI_list = [j for j in VOI_list if j not in {0, 130, 258, 165, 257}]
                    
                    # Isolare tutte le VOI, trasferirle sulla PET e calcolare media e std dei conteggi in tale VOI
                    FDGPET_wb_array_VOI_i_mean, FDGPET_wb_array_VOI_i_std, FDGPET_pons_array_VOI_i_mean, FDGPET_pons_array_VOI_i_std = ([] for i in range(4))
                    for i in VOI_list:
                        VOI_i = np.isin(SEG_array_cropped, [i]) #plt.imshow(VOI_i[:,:,150])
                        FDGPET_wb_array_VOI_i = FDGPET_wb_array[VOI_i]
                        FDGPET_wb_array_VOI_i_mean.append(np.mean(FDGPET_wb_array_VOI_i))
                        FDGPET_wb_array_VOI_i_std.append(np.std(FDGPET_wb_array_VOI_i))
                        FDGPET_pons_array_VOI_i = FDGPET_pons_array[VOI_i]
                        FDGPET_pons_array_VOI_i_mean.append(np.mean(FDGPET_pons_array_VOI_i))
                        FDGPET_pons_array_VOI_i_std.append(np.std(FDGPET_pons_array_VOI_i))
                    header_fdg = pd.MultiIndex.from_product([[subj_id]])
                    df_VOI_fdg_wbmean = (pd.DataFrame(FDGPET_wb_array_VOI_i_mean, index=VOI_list, columns=header_fdg)).round(3)
                    df_VOI_fdg_wbstd = (pd.DataFrame(FDGPET_wb_array_VOI_i_std, index=VOI_list, columns=header_fdg)).round(3)
                    df_VOI_fdg_ponsmean = (pd.DataFrame(FDGPET_pons_array_VOI_i_mean, index=VOI_list, columns=header_fdg)).round(3)
                    df_VOI_fdg_ponsstd = (pd.DataFrame(FDGPET_pons_array_VOI_i_std, index=VOI_list, columns=header_fdg)).round(3)
                    df_VOI_fdg_subj_wbmean = pd.concat([df_VOI_fdg_subj_wbmean, df_VOI_fdg_wbmean], axis=1)
                    df_VOI_fdg_subj_wbstd = pd.concat([df_VOI_fdg_subj_wbstd, df_VOI_fdg_wbstd], axis=1)
                    df_VOI_fdg_subj_ponsmean = pd.concat([df_VOI_fdg_subj_ponsmean, df_VOI_fdg_ponsmean], axis=1)
                    df_VOI_fdg_subj_ponsstd = pd.concat([df_VOI_fdg_subj_ponsstd, df_VOI_fdg_ponsstd], axis=1)
                    print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
                    f1 = open(path_project + 'logSubjects_RegAnalFDG.txt', 'a')
                    f1.write("RegAnalFDG complete for subject " + subj_id + "\n")
                    f1.close()
                else:
                    print("Unable to run RegAnalFDG. FDG-PET is missing in Subject", subj_id)
                    f2 = open(path_project + 'logSubjects_RegAnalFDG_warning.txt', 'a')
                    f2.write("Unable to run RegAnalFDG. FDG-PET is missing in Subject " + subj_id + "\n")
                    f2.close()
            else:
                print("Unable to run RegAnalFDG. Atlas is missing in Subject", subj_id)
                f2 = open(path_project + 'logSubjects_RegAnalFDG_warning.txt', 'a')
                f2.write("Unable to run RegAnalFDG. Atlas is missing in Subject " + subj_id + "\n")
                f2.close()
    df_VOI_fdg = pd.concat([df_VOI_fdg_subj_wbmean.transpose(),df_VOI_fdg_subj_wbstd.transpose(),df_VOI_fdg_subj_ponsmean.transpose(),df_VOI_fdg_subj_ponsstd.transpose()], axis=1)
    df_VOI_fdg.to_excel(path_project + 'tabella_RegAnalFDG.xlsx')
