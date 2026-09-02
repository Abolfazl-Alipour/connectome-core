"""
Module: consensus
Computes group-level consensus connectomes across cohort using non-parametric
element-wise median aggregation and strict 3-sigma SIFT2 mu outlier rejection.
"""

import os
import glob
import numpy as np
from typing import List, Tuple, Dict

def compute_group_consensus(
    connectomes_dir: str,
    output_dir: str,
    resolutions: List[int],
    prefix: str = "",
    min_streamline_count: int = 3,
    mu_sigma_threshold: float = 3.0
) -> Dict[int, Dict[str, str]]:
    """
    Builds element-wise median group consensus matrices for SIFT2, Length, and Prevalence.

    Parameters
    ----------
    connectomes_dir : str
        Directory containing subject subfolders or connectome files.
    output_dir : str
        Target directory for group consensus outputs.
    resolutions : list of int
        Atlas resolutions to compute.
    min_streamline_count : int
        Minimum streamlines required to define a valid structural connection.
    mu_sigma_threshold : float
        Outlier threshold for subject SIFT2 proportionality coefficient (mu).

    Returns
    -------
    dict
        Dictionary mapping resolution to exported file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Discover subjects and load Mu values
    subject_dirs = sorted([d for d in glob.glob(os.path.join(connectomes_dir, "*")) if os.path.isdir(d)])
    subjects = [os.path.basename(d) for d in subject_dirs if os.path.exists(os.path.join(d, f"{os.path.basename(d)}_sift_mu.txt"))]
    
    if not subjects:
        # Fallback if flat structure
        mu_files = sorted(glob.glob(os.path.join(connectomes_dir, "*_sift_mu.txt")))
        subjects = [os.path.basename(f).replace("_sift_mu.txt", "") for f in mu_files]
        subject_dirs = [connectomes_dir] * len(subjects)

    print(f"Discovered {len(subjects)} subjects with SIFT2 mu files.")
    
    mu_values = []
    valid_subjects = []
    
    for s, s_dir in zip(subjects, subject_dirs):
        mu_file = os.path.join(s_dir, f"{s}_sift_mu.txt") if s_dir != connectomes_dir else os.path.join(connectomes_dir, f"{s}_sift_mu.txt")
        try:
            val = float(open(mu_file).read().strip())
            mu_values.append(val)
            valid_subjects.append((s, s_dir, val))
        except Exception:
            continue
            
    mu_arr = np.array(mu_values)
    mean_mu = np.mean(mu_arr)
    std_mu = np.std(mu_arr)
    
    # 2. Filter outliers (>3 sigma)
    cohort = []
    outliers = []
    for s, s_dir, val in valid_subjects:
        if abs(val - mean_mu) <= mu_sigma_threshold * std_mu:
            cohort.append((s, s_dir, val))
        else:
            outliers.append((s, val))
            
    print(f"Cohort QC: Retained {len(cohort)} subjects, Rejected {len(outliers)} outliers (> {mu_sigma_threshold} sigma).")
    
    results = {}
    
    # 3. Compute Median Consensus per resolution
    for res in resolutions:
        print(f"\nProcessing Group Consensus for Resolution: {res}")
        sift_stack = []
        length_stack = []
        prev_stack = []
        
        for s, s_dir, mu_val in cohort:
            file_base = os.path.join(s_dir, f"{s}_{prefix}{res}" if prefix else f"{s}_{res}") if s_dir != connectomes_dir else os.path.join(connectomes_dir, f"{s}_{prefix}{res}" if prefix else f"{s}_{res}")
            
            sift_file = f"{file_base}_sift.csv"
            length_file = f"{file_base}_mean_length.csv"
            count_file = f"{file_base}_count.csv"
            
            if not (os.path.exists(sift_file) and os.path.exists(length_file) and os.path.exists(count_file)):
                continue
                
            sift = np.loadtxt(sift_file, delimiter=",")
            length = np.loadtxt(length_file, delimiter=",")
            count = np.loadtxt(count_file, delimiter=",")
            
            # Apply count threshold
            mask = (count >= min_streamline_count)
            sift_scaled = sift * mu_val * mask
            length_masked = length * mask
            
            sift_stack.append(sift_scaled)
            length_stack.append(length_masked)
            prev_stack.append(mask.astype(float))
            
        if not sift_stack:
            print(f"  [WARN] No matrices found for resolution {res}. Skipping.")
            continue
            
        sift_arr = np.array(sift_stack)
        length_arr = np.array(length_stack)
        prev_arr = np.array(prev_stack)
        
        # Non-parametric Median Consensus (including structural zeros)
        median_sift = np.median(sift_arr, axis=0)
        median_length = np.median(length_arr, axis=0)
        prevalence = np.mean(prev_arr, axis=0)
        
        out_sift = os.path.join(output_dir, f"group_mean_sift_{res}.csv")
        out_length = os.path.join(output_dir, f"group_mean_length_{res}.csv")
        out_prev = os.path.join(output_dir, f"group_prevalence_{res}.csv")
        
        np.savetxt(out_sift, median_sift, delimiter=",", fmt="%.8f")
        np.savetxt(out_length, median_length, delimiter=",", fmt="%.8f")
        np.savetxt(out_prev, prevalence, delimiter=",", fmt="%.8f")
        
        results[res] = {"sift": out_sift, "length": out_length, "prevalence": out_prev}
        print(f"  [SUCCESS] Exported Median Consensus matrices for {res} to {output_dir}")
        
    return results
