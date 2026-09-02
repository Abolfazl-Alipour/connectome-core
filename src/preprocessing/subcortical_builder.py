"""
Module: subcortical_builder
Builds hybrid cortical-subcortical parcellations by integrating FSL FIRST segmentations
with Schaefer 7-network cortical parcels.
"""

import os
import nibabel as nib
import numpy as np

# Standard FSL FIRST anatomical label values
FSL_SUBCORTICAL_LABELS = [
    10,  # Left-Thalamus-Proper
    11,  # Left-Caudate
    12,  # Left-Putamen
    13,  # Left-Pallidum
    17,  # Left-Hippocampus
    18,  # Left-Amygdala
    26,  # Left-Accumbens-area
    49,  # Right-Thalamus-Proper
    50,  # Right-Caudate
    51,  # Right-Putamen
    52,  # Right-Pallidum
    53,  # Right-Hippocampus
    54,  # Right-Amygdala
    58,  # Right-Accumbens-area
]

def build_hybrid_parcellation(cortical_nii_path: str, first_seg_path: str, output_nii_path: str, cortex_nodes: int) -> str:
    """
    Combines a Schaefer cortical parcellation volume (labels 1..N) with 14 subcortical regions
    from FSL FIRST, assigning subcortical structures continuous labels (N+1 .. N+14).

    Parameters
    ----------
    cortical_nii_path : str
        Path to the cortical NIfTI parcellation image.
    first_seg_path : str
        Path to the FSL FIRST segmentation NIfTI image (`_all_fast_firstseg.nii.gz`).
    output_nii_path : str
        Output path for the combined parcellation volume.
    cortex_nodes : int
        Number of cortical parcels (e.g. 600, 700, 800, 900, 1000).

    Returns
    -------
    str
        Path to the written hybrid parcellation image.
    """
    cortex_img = nib.load(cortical_nii_path)
    cortex_data = cortex_img.get_fdata().astype(np.int32)
    
    first_img = nib.load(first_seg_path)
    first_data = first_img.get_fdata().astype(np.int32)
    
    combined_data = cortex_data.copy()
    
    for idx, fsl_val in enumerate(FSL_SUBCORTICAL_LABELS):
        new_label = cortex_nodes + 1 + idx
        # Subcortical segmentation overwrites background or overlaps
        mask = (first_data == fsl_val)
        combined_data[mask] = new_label
        
    out_img = nib.Nifti1Image(combined_data, cortex_img.affine, cortex_img.header)
    os.makedirs(os.path.dirname(os.path.abspath(output_nii_path)), exist_ok=True)
    nib.save(out_img, output_nii_path)
    return output_nii_path
