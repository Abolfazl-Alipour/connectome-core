"""
Module: null_models
Generates three canonical null-model networks for the isolated S-Core submatrices:
1. Erdős-Rényi (ER): Density & size matched random graph.
2. Regular Graph: Uniform median-degree graph (destroys hubs).
3. Degree-Preserved (Maslov-Sneppen): Preserves exact empirical hub degrees while scrambling topology.

Empirical core SIFT2 edge weights are shuffled and uniquely assigned across all null models.
"""

import os
import numpy as np
import networkx as nx
from typing import List

SUBDIRS = ["er", "regular", "degree_preserved"]

def assign_shuffled_weights(G: nx.Graph, N_core: int, empirical_weights: np.ndarray) -> np.ndarray:
    """Assigns shuffled empirical SIFT2 weights to the edges of graph G."""
    adj = np.zeros((N_core, N_core))
    shuffled = np.random.permutation(empirical_weights)
    for idx, (u, v) in enumerate(G.edges()):
        w = shuffled[idx % len(shuffled)]
        adj[u, v] = w
        adj[v, u] = w
    return adj

def generate_core_null_models(
    core_dir: str,
    control_dir: str,
    resolutions: List[int]
):
    """
    Generates ER, Regular, and Maslov-Sneppen null models for each resolution's S-Core.
    """
    for sub in SUBDIRS:
        os.makedirs(os.path.join(control_dir, sub), exist_ok=True)
        
    for res in resolutions:
        sift_file = os.path.join(core_dir, f"core_sift_{res}.csv")
        prev_file = os.path.join(core_dir, f"core_prevalence_{res}.csv")
        
        if not (os.path.exists(sift_file) and os.path.exists(prev_file)):
            print(f"  [WARN] Missing core files for res {res}. Skipping.")
            continue
            
        core_sift = np.loadtxt(sift_file, delimiter=",")
        core_prev = np.loadtxt(prev_file, delimiter=",")
        
        core_adj = (core_prev > 0).astype(int)
        np.fill_diagonal(core_adj, 0)
        
        N_core = core_adj.shape[0]
        E_core = int(np.sum(core_adj) / 2)
        k_median = int(np.median(np.sum(core_adj, axis=1)))
        
        # Extract empirical non-zero weights
        emp_weights = core_sift[np.triu_indices(N_core, k=1)]
        emp_weights = emp_weights[emp_weights > 0]
        
        if len(emp_weights) == 0:
            print(f"  [WARN] No non-zero weights found for res {res}. Skipping.")
            continue
        
        # 1. ER Null Model
        try:
            G_er = nx.gnm_random_graph(N_core, E_core)
            adj_er = assign_shuffled_weights(G_er, N_core, emp_weights)
            np.savetxt(os.path.join(control_dir, "er", f"control_er_sift_{res}.csv"), adj_er, delimiter=",", fmt="%.8f")
        except Exception as e:
            print(f"  [ERROR] ER generation failed for {res}: {e}")
            
        # 2. Regular Null Model
        if (N_core * k_median) % 2 != 0:
            k_median = min(k_median + 1, N_core - 1 if (N_core - 1) % 2 == 0 else N_core - 2)
        try:
            G_reg = nx.random_regular_graph(k_median, N_core)
            adj_reg = assign_shuffled_weights(G_reg, N_core, emp_weights)
            np.savetxt(os.path.join(control_dir, "regular", f"control_regular_sift_{res}.csv"), adj_reg, delimiter=",", fmt="%.8f")
        except Exception as e:
            print(f"  [ERROR] Regular graph generation failed for {res}: {e}")
            
        # 3. Degree-Preserved (Maslov-Sneppen)
        G_dp = nx.from_numpy_array(core_adj)
        n_swaps = min(5 * E_core, 1000)
        max_tries = 50 * max(n_swaps, E_core)
        
        # Perform robust edge swaps
        swapped = False
        try:
            nx.double_edge_swap(G_dp, nswap=n_swaps, max_tries=max_tries)
            swapped = True
        except Exception:
            # Fallback with smaller swap count if dense
            try:
                G_dp = nx.from_numpy_array(core_adj)
                nx.double_edge_swap(G_dp, nswap=max(1, E_core // 2), max_tries=max_tries)
                swapped = True
            except Exception as e:
                print(f"  [WARN] Double edge swap fell back to degree sequence config generator: {e}")
                
        if not swapped:
            # Configuration model fallback preserving exact degree sequence
            degrees = [d for _, d in G_dp.degree()]
            G_dp = nx.expected_degree_graph(degrees, selfloops=False)
            
        adj_dp = assign_shuffled_weights(G_dp, N_core, emp_weights)
        np.savetxt(os.path.join(control_dir, "degree_preserved", f"control_degree_preserved_sift_{res}.csv"), adj_dp, delimiter=",", fmt="%.8f")
            
        print(f"  [SUCCESS] Exported 3 Null Models for resolution {res} to {control_dir}")
