"""
Module: annotations
Exports full-brain annotated connectomes with the master core_node_annotations.csv
mapping file for Paradigm A whole-brain dynamical simulations.
"""

import os
import shutil
import csv
import numpy as np
from typing import List

def export_annotated_connectomes(
    group_dir: str,
    core_dir: str,
    out_dir: str,
    resolutions: List[int]
) -> str:
    """
    Copies whole-brain matrices and generates core_node_annotations.csv
    mapping every node to Is_Core (1 or 0).
    """
    os.makedirs(out_dir, exist_ok=True)
    master_csv = os.path.join(out_dir, "core_node_annotations.csv")
    
    with open(master_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Resolution", "Node_Index", "Is_Core"])
        
        for res in resolutions:
            # Copy consensus files
            for metric in ["sift", "length", "prevalence"]:
                fname = f"group_mean_{metric}_{res}.csv" if metric != "prevalence" else f"group_prevalence_{res}.csv"
                src = os.path.join(group_dir, fname)
                dst = os.path.join(out_dir, fname)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    
            # Load core indices
            indices_file = os.path.join(core_dir, f"core_node_indices_{res}.csv")
            core_indices = set(np.loadtxt(indices_file, delimiter=",", dtype=int)) if os.path.exists(indices_file) else set()
            
            # Write annotations
            for node_idx in range(res):
                writer.writerow([res, node_idx, 1 if node_idx in core_indices else 0])
                
    print(f"Master annotation mapping written to: {master_csv}")
    return master_csv
