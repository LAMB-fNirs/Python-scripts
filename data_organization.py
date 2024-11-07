# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: nirs_env
#     language: python
#     name: python3
# ---

# %%
import os
import numpy as np
import mne
from mne.io import read_raw_nirx
import tkinter as tk
from tkinter import filedialog
import h5py
from pathlib import Path
import shutil
import os
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import shutil

# %%
path = '<PATH_TO_NIRS_FILES>'

# Path where your .nirs files are located
nirs_files = [path+'/'+f for f in os.listdir(path) if f.endswith('.nirs')]


def generate_stimulus_points(files):
    for file in files:
        data = sio.loadmat(file)  # Load .nirs (MATLAB) file

        # Extract 'aux' data assuming the column structure matches
        aux = data.get('aux')
        if aux is None or aux.shape[1] < 4:
            print(f"Error: `aux` data not found or does not have expected columns in {file}")
            continue

        # Process stimulus points: select columns 2:4, binarize values as in the original script
        s = aux[:, 1:4]
        s[s > 1] = 1
        s[s < 1] = 0

        # Save the updated data back into the file
        data['s'] = s
        sio.savemat(file, data)
        print(f"{file} completed...")

# 2. Plot Stimulus Points for Each Participant
def plot_stimulus_points(files):
    plt.figure(figsize=(15, 10))
    for i, file in enumerate(files, start=1):
        data = sio.loadmat(file)
        s = data.get('s')
        t = data.get('t')

        if s is None or t is None:
            print(f"Error: `s` or `t` data not found in {file}")
            continue

        # Plot in a 10x2 grid, similar to MATLAB's subplot(10,2,i)
        plt.subplot(10, 2, i)
        plt.plot(t, s)
        plt.title(file)
    
    plt.tight_layout()
    plt.show()


def organize_files_into_subject_folders(files, start_num=100):
    for i, file in enumerate(files, start=0):
        subject_folder = f"Subject{start_num + i}"
        
        # Create subject folder if it doesn't exist
        os.makedirs(subject_folder, exist_ok=True)
        
        # Move the file into the subject folder
        print(file , os.path.join(subject_folder, file.split('/')[-1]))
        shutil.copy(file, os.path.join(subject_folder, file.split('/')[-1]))
        print(f"Moved {file} to {subject_folder}")

# Run the functions
generate_stimulus_points(nirs_files)
plot_stimulus_points(nirs_files)
organize_files_into_subject_folders(nirs_files)




# %%
