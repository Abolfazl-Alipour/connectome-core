"""
Module: score
Extracts the S-Core (Anatomical Strength Core) by ranking nodes by continuous SIFT2
bandwidth, isolating the top 15% structural hubs, and extracting the Giant Connected Component.
"""

import os
import json
import numpy as np
import networkx as nx
from typing import List, Dict

def extract_score(
    in_dir: str,
    out_dir: str,
    resolutions: List[int],
    retention_percentage: float = 0.15
) -> Dict[int, Dict[str, any]]:
    """
    Extracts the isolated S-Core submatrices for given resolutions.

    Parameters
    ----------
    in_dir : str
        Directory with group consensus connectomes (`group_mean_sift_{res}.csv`, etc.)
    out_dir : str
        Output directory for isolated `group_cores/` submatrices.
    resolutions : list of int
        Atlas resolutions to process.
    retention_percentage : float
        Fraction of strongest nodes to retain (default: 0.15 for top 15%).

    Returns
    -------
    dict
        Metadata and metrics for each resolution's S-Core.
    """
    os.makedirs(out_dir, exist_ok=True)
    summary_stats = {}
    
    for res in resolutions:
        print(f"\nProcessing S-Core for Resolution: {res}")
        
        prev_file = os.path.join(in_dir, f"group_prevalence_{res}.csv")
        sift_file = os.path.join(in_dir, f"group_mean_sift_{res}.csv")
        length_file = os.path.join(in_dir, f"group_mean_length_{res}.csv")
        
        if not all([os.path.exists(f) for f in [prev_file, sift_file, length_file]]):
            print(f"  [ERROR] Missing consensus matrices for {res}. Skipping.")
            continue
            
        prev_mat = np.loadtxt(prev_file, delimiter=",")
        sift_mat = np.loadtxt(sift_file, delimiter=",")
        length_mat = np.loadtxt(length_file, delimiter=",")
        
        N = prev_mat.shape[0]
        
        # 1. Continuous Node Strength (S-Core)
        node_strength = np.sum(sift_mat, axis=1)
        
        # 2. Fractional Ranking
        target_k = int(N * retention_percentage)
        top_indices = np.argsort(node_strength)[::-1][:target_k]
        
        # 3. Giant Connected Component (GCC) Extraction
        sub_prev = prev_mat[np.ix_(top_indices, top_indices)]
        adj_matrix = (sub_prev > 0).astype(int)
        np.fill_diagonal(adj_matrix, 0)
        
        G = nx.from_numpy_array(adj_matrix)
        components = list(nx.connected_components(G))
        
        if len(components) == 0:
            print(f"  [ERROR] Core is completely disconnected for {res}.")
            continue
            
        largest_cc = max(components, key=len)
        gcc_size = len(largest_cc)
        
        final_core_indices = sorted([top_indices[idx] for idx in largest_cc])
        
        # 4. Strict Submatrix Slicing (N_core x N_core)
        core_sift = sift_mat[np.ix_(final_core_indices, final_core_indices)]
        core_length = length_mat[np.ix_(final_core_indices, final_core_indices)]
        core_prev = prev_mat[np.ix_(final_core_indices, final_core_indices)]
        
        possible_edges = gcc_size * (gcc_size - 1)
        actual_edges = np.sum(core_prev > 0)
        density = actual_edges / possible_edges if possible_edges > 0 else 0
        
        # Export
        out_indices = os.path.join(out_dir, f"core_node_indices_{res}.csv")
        out_sift = os.path.join(out_dir, f"core_sift_{res}.csv")
        out_length = os.path.join(out_dir, f"core_length_{res}.csv")
        out_prev = os.path.join(out_dir, f"core_prevalence_{res}.csv")
        out_stats = os.path.join(out_dir, f"core_stats_{res}.json")
        
        np.savetxt(out_indices, final_core_indices, delimiter=",", fmt="%d")
        np.savetxt(out_sift, core_sift, delimiter=",", fmt="%.8f")
        np.savetxt(out_length, core_length, delimiter=",", fmt="%.8f")
        np.savetxt(out_prev, core_prev, delimiter=",", fmt="%.8f")
        
        stats = {
            "resolution": res,
            "retention_percentage": retention_percentage,
            "base_nodes": N,
            "target_core_nodes": target_k,
            "final_gcc_nodes": gcc_size,
            "core_edge_density": density,
            "min_core_strength": float(np.min(node_strength[final_core_indices])),
            "max_core_strength": float(np.max(node_strength[final_core_indices]))
        }
        with open(out_stats, 'w') as f:
            json.dump(stats, f, indent=4)
            
        summary_stats[res] = stats
        print(f"  [SUCCESS] Exported N_core={gcc_size} S-Core submatrices to {out_dir}")
        
    return summary_stats
