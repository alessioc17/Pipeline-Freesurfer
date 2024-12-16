#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 09:56:24 2024

@authors: alessio cirone; cristina campi; sara garbarino

@email: alessio.cirone@hsanmartino.it; campi@dima.unige.it; garbarino@dima.unige.it
"""

import os
import pandas as pd
import subprocess
from pathlib import Path

# Configure environment variables
os.environ['FREESURFER_HOME'] = '/usr/local/freesurfer/7-dev/'

def write_subject_list(subj_list, output_file):
    """Writes the list of subjects to a file, excluding 'fsaverage'."""
    with open(output_file, 'w') as file:
        for subj in subj_list:
            if subj != 'fsaverage':
                file.write(f"{subj}\n")

def run_freesurfer_command(command, **kwargs):
    """Executes a FreeSurfer command with error handling."""
    try:
        subprocess.run(command, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        print(f"Error while executing the command: {command}")
        raise e

def create_excel_with_sheets(output_file, dataframes):
    """Writes the DataFrames to an Excel file with separate sheets."""
    with pd.ExcelWriter(output_file) as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name)

if __name__ == '__main__':
    # Main paths
    path_project = Path('/mnt/d/Dati_AMYITA/AD_Atipici_Cecchin/')
    path_data = path_project / 'data_finale/'
    os.environ['SUBJECTS_DIR'] = str(path_data)
    
    # Generate subject list
    subj_list = sorted(path_data.iterdir())
    subj_list = [subj.name for subj in subj_list if subj.is_dir()]
    subj_list_file = path_project / 'subj_List.txt'
    write_subject_list(subj_list, subj_list_file)

    # Run FreeSurfer commands
    commands = [
        ["asegstats2table", "--subjectsfile", subj_list_file, "--meas", "volume", "--tablefile", "aseg.txt", "--skip"],
        ["aparcstats2table", "--subjectsfile", subj_list_file, "--hemi", "rh", "--meas", "thickness", "--tablefile", "rh_aparc.txt", "--skip"],
        ["aparcstats2table", "--subjectsfile", subj_list_file, "--hemi", "lh", "--meas", "thickness", "--tablefile", "lh_aparc.txt", "--skip"]
    ]
    for command in commands:
        run_freesurfer_command(command)
    
    # Load data and write Excel
    dataframes = {
        "Subcortical Volumes": pd.read_csv("aseg.txt", sep='\t'),
        "Cortical Thickness rh": pd.read_csv("rh_aparc.txt", sep='\t'),
        "Cortical Thickness lh": pd.read_csv("lh_aparc.txt", sep='\t')
    }
    create_excel_with_sheets(path_project / 'MRI_table.xlsx', dataframes)
