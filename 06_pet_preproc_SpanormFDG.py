# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:17:57 2023

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import sys, os, time
from nipype.interfaces.freesurfer import MRIConvert
from nipype.interfaces.ants import RegistrationSynQuick, ApplyTransforms
from multiprocessing import cpu_count
from joblib import Parallel, delayed
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7.4.1/'

def ciclo_spanormFDG(subj_id, path_data):
    if subj_id[0] != '.' and subj_id != 'fsaverage':
        
        # MRI -> MNI (deformable b-spline syn)
        MNI_T1 = path_project + 'mni/mni_icbm152_t1_tal_nlin_sym_55_ext.nii'
        MRI_T1 = path_data + subj_id + '/mri/orig/001.nii'
        if os.path.exists(MRI_T1):
            mri_registered = path_data + subj_id + '/mri/norm/'
            if not os.path.exists(mri_registered):
                os.makedirs(mri_registered)
            os.chdir(mri_registered)
            reg_MR = RegistrationSynQuick()
            reg_MR.inputs.fixed_image = MNI_T1
            reg_MR.inputs.moving_image = MRI_T1
            reg_MR.inputs.transform_type = "b" 
            reg_MR.inputs.output_prefix = 'MRonMNI_'
            reg_MR.run()
            
        ### Seg -> MNI
        seg = path_data + subj_id + '/mri/aparc+aseg.mgz'
        if os.path.exists(seg):
            segconv = MRIConvert()
            segconv.inputs.in_file = seg
            segconv.inputs.out_file = path_data + subj_id + '/mri/aparc+aseg.nii.gz'
            segconv.inputs.out_type = 'niigz'
            segconv.run()
            at_seg = ApplyTransforms()
            at_seg.inputs.input_image = path_data + subj_id + '/mri/aparc+aseg.nii.gz'
            at_seg.inputs.reference_image = MNI_T1
            at_seg.inputs.output_image = path_data + subj_id + '/mri/aparc+aseg_on_mni.nii.gz'
            at_seg.inputs.transforms = [mri_registered + 'MRonMNI_1Warp.nii.gz', mri_registered + 'MRonMNI_0GenericAffine.mat']
            at_seg.inputs.interpolation = 'NearestNeighbor'
            at_seg.run()
                    
            ### PET -> MNI
            pet = path_data + subj_id + '/amypet/orig/amy.nii'
            if os.path.exists(pet):
                pet_registered = path_data + subj_id + '/amypet/norm/'
                if not os.path.exists(pet_registered):
                    os.makedirs(pet_registered)
                os.chdir(pet_registered)
                reg_fdg = RegistrationSynQuick()
                reg_fdg.inputs.fixed_image = MRI_T1
                reg_fdg.inputs.moving_image = pet
                reg_fdg.inputs.transform_type = "a"
                reg_fdg.inputs.output_prefix = 'AMYPETonMR_'
                reg_fdg.run()
                at_fdg = ApplyTransforms()
                at_fdg.inputs.input_image = 'AMYPETonMR_Warped.nii.gz'
                at_fdg.inputs.reference_image = MNI_T1
                at_fdg.inputs.output_image = 'AMYPETonMNI.nii.gz'
                at_fdg.inputs.transforms = [mri_registered + 'MRonMNI_1Warp.nii.gz', mri_registered + 'MRonMNI_0GenericAffine.mat']
                at_fdg.run()
                
                print("\n" + "########### " + "Subject " + subj_id + " complete " + "###########" + "\n")
                f1 = open(path_project + 'logSubjects_spanorm.txt', 'a')
                f1.write("Spanorm complete for subject " + subj_id + "\n")
                f1.close()
            else:
                print("Unable to run Spanorm. PET is missing in Subject", subj_id)
                f2 = open(path_project + 'logSubjects_spanorm_warning.txt', 'a')
                f2.write("Unable to run Spanorm. PET is missing in Subject " + subj_id + "\n")
                f2.close()
        else:
            print("Unable to run SpanormFDG. gtmseg is missing in Subject", subj_id)
            f2 = open(path_project + 'logSubjects_spanormFDG_warning.txt', 'a')
            f2.write("Unable to run SpanormFDG. GTMSeg is missing in Subject " + subj_id + "\n")
            f2.close()

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    path_project = '/home/shared/LISCOMP/PD_HSM/'
    path_data = path_project + 'data/'
    MNI_T1 = '/home/shared/LISCOMP/Healthy_MNI/mni_icbm152_t1_tal_nlin_sym_55_ext.nii.gz'
    os.environ['SUBJECTS_DIR'] = path_data
    subj_List = sorted(os.listdir(path_data))
    start_time = time.time()
    ris = Parallel(n_jobs=int(cpu_count()))(delayed(ciclo_spanormFDG)(subj_id, path_data) for subj_id in subj_List)
    print("--- %s seconds ---" % (time.time() - start_time))
    
############
# These results have been obtained using an homemade pipeline. This pipeline first performs 
# intra-subject affine registration of the PET image into the space of the subject’s T1-weighted
# (T1w) MR image using the SyN algorithm [Avants et al., 2008] from ANTs [Avants et al., 2014].
# The PET to T1w transformation is then composed with T1w to ICBM 2009c nonlinear symmetric template
# deformable transformation, to transport the PET image to the MNI space [Fonov et al., 2011, 2009].
# The PET image is further intensity normalized using the average PET uptake in a reference region
# (pons/wb for FDG PET, cerebellum/wb for amyloid PET), resulting in a standardized uptake value ratio (SUVR) map.
