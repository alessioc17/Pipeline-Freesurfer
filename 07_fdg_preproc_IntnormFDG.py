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
import mahotas
from multiprocessing import cpu_count
from joblib import Parallel, delayed
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

def ciclo_intnormFDG(subj_id, path_data):
    if subj_id[0] != '.' and subj_id != 'fsaverage':
        
        # Caricare segmentazione e PET FDG
        SEG = path_data + subj_id + '/mri/gtmseg_on_mni.nii.gz'
        if os.path.exists(SEG):
            SEG_im = nib.load(SEG)
            SEG_array = nib.load(SEG).get_fdata(dtype="float32")
            FDGPET = path_data + subj_id + '/fdgpet/norm/FDGPETonMNI.nii.gz'
            if os.path.exists(FDGPET):
                FDGPET_im = nib.load(FDGPET)
                FDGPET_array = nib.load(FDGPET).get_fdata(dtype="float32")
                FDGPET_shape = FDGPET_array.shape
                
                # Croppare la segmetazione in modo da allinearla con la PET FDG (esse condividono già il centro RAS)
                FDGPET_orig = [round(FDGPET_im.affine[0][3], 2), round(FDGPET_im.affine[1][3], 2), round(FDGPET_im.affine[2][3], 2)]
                SEG_orig = [round(SEG_im.affine[0][3], 2), round(SEG_im.affine[1][3], 2), round(SEG_im.affine[2][3], 2)]
                left = round(abs(SEG_orig[0] - FDGPET_orig[0]))
                bottom = round(abs(SEG_orig[1] - FDGPET_orig[1]))
                inferior = round(abs(SEG_orig[2] - FDGPET_orig[2]))
                SEG_array_cropped = SEG_array[left : left + FDGPET_shape[0], bottom : bottom + FDGPET_shape[1], inferior : inferior + FDGPET_shape[2]]
                
                # Isolare la VOI di riferimento e contrarla per ridurre gli effetti di bordo dovuti alla registrazione
                wb_VOI = np.isin(SEG_array_cropped, [0, 130, 258, 165, 257], invert=True)
                wb_perim = mahotas.bwperim(wb_VOI)
                wb_eroded = np.bitwise_xor(wb_VOI, wb_perim)
                wb_eroded_im = nib.Nifti1Image((wb_eroded*1).astype(np.int32), affine=FDGPET_im.affine)
                nib.save(wb_eroded_im, path_data + subj_id + '/fdgpet/norm/Wb_eroded_FDGPETonMNI.nii.gz')
                pons_VOI = SEG_array_cropped == 174 # plt.imshow(pons_VOI[:,:,40])
                pons_perim = mahotas.bwperim(pons_VOI)
                pons_eroded = np.bitwise_xor(pons_VOI, pons_perim)
                pons_eroded_im = nib.Nifti1Image((pons_eroded*1).astype(np.int32), affine=FDGPET_im.affine)
                nib.save(pons_eroded_im, path_data + subj_id + '/fdgpet/norm/Pons_eroded_FDGPETonMNI.nii.gz')
                
                # Trasferire la VOI sulla PET FDG e calcolare la media dei conteggi in tale VOI
                FDGPET_array_wb = FDGPET_array[wb_eroded]
                FDGPET_array_wb_mean = np.mean(FDGPET_array_wb)
                FDGPET_array_pons = FDGPET_array[pons_eroded]
                FDGPET_array_pons_mean = np.mean(FDGPET_array_pons)
                
                # Dividere i conteggi della PET per il valore medio di uptake nella VOI di riferimento (SUVR)
                FDGPET_array_norm_wb = FDGPET_array/FDGPET_array_wb_mean
                FDGPET_im_norm_wb = nib.Nifti1Image(FDGPET_array_norm_wb, affine=FDGPET_im.affine)
                nib.save(FDGPET_im_norm_wb, path_data + subj_id + '/fdgpet/norm/FDGPETonMNI_intnorm_wb.nii.gz')
                FDGPET_array_norm_pons = FDGPET_array/FDGPET_array_pons_mean
                FDGPET_im_norm_pons = nib.Nifti1Image(FDGPET_array_norm_pons, affine=FDGPET_im.affine)
                nib.save(FDGPET_im_norm_pons, path_data + subj_id + '/fdgpet/norm/FDGPETonMNI_intnorm_pons.nii.gz')
                print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
                f1 = open(path_project + 'logSubjects_intnormFDG.txt', 'a')
                f1.write("IntnormFDG complete for subject " + subj_id + "\n")
                f1.close()
            else:
                print("Unable to run IntnormFDG. FDG-PET is missing in Subject", subj_id)
                f2 = open(path_project + 'logSubjects_intnormFDG_warning.txt', 'a')
                f2.write("Unable to run IntnormFDG. FDG-PET is missing in Subject " + subj_id + "\n")
                f2.close()   
        else:
            print("Unable to run IntnormFDG. Atlas is missing in Subject", subj_id)
            f2 = open(path_project + 'logSubjects_intnormFDG_warning.txt', 'a')
            f2.write("Unable to run IntnormFDG. Atlas is missing in Subject " + subj_id + "\n")
            f2.close()
            
if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    ris = Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_intnormFDG)(subj_id, path_data) for subj_id in subj_List)
