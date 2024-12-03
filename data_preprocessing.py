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
# ---

# %%
import mne
import mne_nirs
import pandas as pd
import numpy as np
from mne.preprocessing.nirs import optical_density, beer_lambert_law
from mne_nirs.statistics import run_GLM
from mne.io import read_raw_nirx
from mne_nirs.experimental_design import make_first_level_design_matrix
from mne.datasets import sample
import scipy.io as sio
import os
import h5py
# from mne_nirs.channels import source_detector_distances
import glob
from mne_nirs.channels import get_long_channels, get_short_channels, picks_pair_to_idx
from mne_nirs.experimental_design import make_first_level_design_matrix
from mne_nirs.statistics import run_glm

# %%
nirs_data_dir = '<PATH_TO_SNIRF_FILES>'
raw_data_list = []
nirs_files = glob.glob(f"{nirs_data_dir}/*.snirf")

for nirs_file in nirs_files:
    with h5py.File(nirs_file, "r+") as f:
    # Navigate to the metaDataTags group
        meta_data_tags = f["nirs/metaDataTags"]

    # Check if LengthUnit exists
        if "LengthUnit" not in meta_data_tags:
        # Add LengthUnit as "m" (meters) or another appropriate unit
            meta_data_tags.create_dataset("LengthUnit", data="mm")
        else:
        # Modify the existing LengthUnit if necessary
            meta_data_tags["LengthUnit"][...] = "mm"

raw_data_list = [mne.io.read_raw_snirf(nirs_file, preload=True) for nirs_file in nirs_files]

# %%
raw = mne.concatenate_raws(raw_data_list)
events, event_id = mne.events_from_annotations(raw)

# %%
'''
Under progress, Have to look into ways on how to clean up events whose duration do not criteria
'''
cleaned_events = []
for event in events:
    duration = event[-1]
    if duration == 0.14 or duration == 0.16:
        cleaned_events.append(event)
events = np.array(cleaned_events)

# %%
raw.resample(2)
raw_od = optical_density(raw)
raw_hb = beer_lambert_law(raw_od)
ch_indices = [10, 11, 14, 15, 18, 19]  
raw_hb.pick(picks=ch_indices)

# %%
events, event_dict = mne.events_from_annotations(raw_hb, verbose=False)
mne.viz.plot_events(events, event_id=event_dict, sfreq=raw_hb.info["sfreq"])

# %%
design_matrix = make_first_level_design_matrix(raw_hb, hrf_model="spm", stim_dur=4.9, drift_order=1)
data_subset = raw_hb.copy().pick(picks=range(2))
glm_est = run_glm(data_subset, design_matrix)
glm_est

# %%
glm_est.plot_topo(conditions=["1", "2", "3"]) #Change the conditions accordingly
