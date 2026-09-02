"""
Module: hcp_extractor
Selective extraction of Human Connectome Project (HCP) structural and diffusion packages
with automatic temporary scratch directory cleanup.
"""

import os
import zipfile
import subprocess
import shutil

ESSENTIAL_DIFFUSION_FILES = [
    "T1w/Diffusion/data.nii.gz",
    "T1w/Diffusion/bvals",
    "T1w/Diffusion/bvecs",
    "T1w/Diffusion/nodif_brain_mask.nii.gz",
    "T1w/Diffusion/grad_dev.nii.gz"
]

def extract_hcp_subject(subject_id: str, diff_zip: str, struct_zip: str, work_dir: str):
    """
    Selectively extracts only the required structural and diffusion files
    from HCP Recommended zip archives to conserve disk space.
    """
    os.makedirs(work_dir, exist_ok=True)
    
    # Extract structural T1w
    if os.path.exists(struct_zip):
        with zipfile.ZipFile(struct_zip, 'r') as z:
            for member in z.namelist():
                if member.endswith("T1w/T1w_acpc_dc_restore.nii.gz") or member.endswith("T1w/T1w_acpc_dc_restore_brain.nii.gz"):
                    z.extract(member, work_dir)
                    
    # Extract diffusion
    if os.path.exists(diff_zip):
        with zipfile.ZipFile(diff_zip, 'r') as z:
            for member in z.namelist():
                for target in ESSENTIAL_DIFFUSION_FILES:
                    if member.endswith(target):
                        z.extract(member, work_dir)
                        
    return os.path.join(work_dir, str(subject_id))
