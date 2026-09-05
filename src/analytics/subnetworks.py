"""
Module: subnetworks
Extracts canonical functional subnetworks (Yeo 7) and consciousness-relevant
subgraphs (Posterior Cortical Hot Zone and Global Neuronal Workspace) from
multi-resolution Schaefer 2018 structural connectomes.
"""

import os
import json
import re
import numpy as np
import networkx as nx
import nilearn.datasets
from typing import List, Dict, Tuple, Optional

YEO_7_NETWORKS = [
    "Visual",
    "Somatomotor",
    "Dorsal_Attention",
    "Salience_Ventral_Attention",
    "Limbic",
    "Control_Frontoparietal",
    "Default_Mode"
]

def get_schaefer_labels(res: int) -> List[str]:
    """Fetches official Schaefer 2018 7-Networks parcel labels for a given resolution."""
    atlas = nilearn.datasets.fetch_atlas_schaefer_2018(n_rois=res, yeo_networks=7)
    # Exclude background (index 0)
    raw_labels = atlas.labels[1:]
    labels = [l.decode('utf-8') if isinstance(l, bytes) else str(l) for l in raw_labels]
    if len(labels) != res:
        raise ValueError(f"Expected {res} labels for Schaefer atlas, got {len(labels)}")
    return labels

def classify_yeo_network(label: str) -> str:
    """Classifies a Schaefer label into one of the canonical 7 Yeo networks."""
    if "_Vis_" in label:
        return "Visual"
    elif "_SomMot_" in label:
        return "Somatomotor"
    elif "_DorsAttn_" in label:
        return "Dorsal_Attention"
    elif "_SalVentAttn_" in label:
        return "Salience_Ventral_Attention"
    elif "_Limbic_" in label:
        return "Limbic"
    elif "_Cont_" in label:
        return "Control_Frontoparietal"
    elif "_Default_" in label:
        return "Default_Mode"
    else:
        raise ValueError(f"Unrecognized network in label: {label}")

def is_posterior_hot_zone(label: str) -> bool:
    """
    Identifies if a parcel belongs to the Posterior Cortical Hot Zone
    as formulated by Koch, Tononi, and Boly (Integrated Information Theory).
    Encompasses parietal, occipital, and temporal sensory/associative regions,
    explicitly excluding the prefrontal cortex.
    """
    # 1. All Visual parcels
    if "_Vis_" in label:
        return True
    
    # 2. Posterior Attention (SPL / IPS)
    if "_DorsAttn_Post_" in label:
        return True
    
    # 3. Posterior Control (Parietal / Precuneus)
    if "_Cont_Par_" in label or "_Cont_pCun_" in label:
        return True
    
    # 4. Posterior Default Mode (Precuneus, PCC, Parietal, Temporal, PHC)
    if any(k in label for k in ["_Default_pCunPCC_", "_Default_Par_", "_Default_Temp_", "_Default_PHC_"]):
        return True
    
    # 5. Temporo-occipital and parietal operculum in Ventral Attention
    if any(k in label for k in ["_SalVentAttn_TempOcc", "_SalVentAttn_ParOper"]):
        return True
    
    return False

def is_global_neuronal_workspace(label: str) -> bool:
    """
    Identifies if a parcel belongs to the Global Neuronal Workspace
    as formulated by Stanislas Dehaene and Jean-Pierre Changeux (GNWT).
    Encompasses the frontoparietal control network, salience/ventral attention,
    and prefrontal projection hubs.
    """
    # 1. Entire Frontoparietal Control Network
    if "_Cont_" in label:
        return True
    
    # 2. Entire Salience / Ventral Attention Network (Anterior Insula / dACC)
    if "_SalVentAttn_" in label:
        return True
    
    # 3. Prefrontal hubs in Default Network
    if any(k in label for k in ["_Default_PFC_", "_Default_PFCdPFCm_", "_Default_PFCv_"]):
        return True
    
    # 4. Frontal Eye Fields in Dorsal Attention
    if "_DorsAttn_FEF_" in label:
        return True
        
    return False

def extract_subnetwork_matrices(
    sift_matrix_path: str,
    length_matrix_path: str,
    output_base_dir: str,
    resolution: int = 1000
) -> Dict[str, Dict]:
    """
    Extracts isolated submatrices, index mappings, and summary statistics
    for all 7 Yeo networks and the 2 consciousness subgraphs.
    """
    os.makedirs(output_base_dir, exist_ok=True)
    
    labels = get_schaefer_labels(resolution)
    W = np.loadtxt(sift_matrix_path, delimiter=",")
    L = np.loadtxt(length_matrix_path, delimiter=",") if os.path.exists(length_matrix_path) else np.zeros_like(W)
    
    # Enforce symmetry and clean diagonals
    W = (W + W.T) / 2.0
    np.fill_diagonal(W, 0.0)
    L = (L + L.T) / 2.0
    np.fill_diagonal(L, 0.0)
    
    if W.shape[0] != resolution:
        raise ValueError(f"Matrix dimension {W.shape[0]} does not match resolution {resolution}")
        
    # Build dictionary of subnetwork memberships
    subnetworks = {net: [] for net in YEO_7_NETWORKS}
    subnetworks["Posterior_Hot_Zone"] = []
    subnetworks["Global_Neuronal_Workspace"] = []
    
    annotations = []
    for idx, label in enumerate(labels):
        net = classify_yeo_network(label)
        subnetworks[net].append(idx)
        
        in_phz = is_posterior_hot_zone(label)
        in_gnw = is_global_neuronal_workspace(label)
        
        if in_phz:
            subnetworks["Posterior_Hot_Zone"].append(idx)
        if in_gnw:
            subnetworks["Global_Neuronal_Workspace"].append(idx)
            
        annotations.append({
            "Node_Index": idx,
            "Parcel_Label": label,
            "Yeo_Network": net,
            "In_Posterior_Hot_Zone": int(in_phz),
            "In_Global_Neuronal_Workspace": int(in_gnw)
        })
        
    # Save master annotation CSV
    ann_path = os.path.join(output_base_dir, f"subnetwork_node_annotations_{resolution}.csv")
    with open(ann_path, "w") as f:
        f.write("Node_Index,Parcel_Label,Yeo_Network,In_Posterior_Hot_Zone,In_Global_Neuronal_Workspace\n")
        for a in annotations:
            f.write(f"{a['Node_Index']},{a['Parcel_Label']},{a['Yeo_Network']},{a['In_Posterior_Hot_Zone']},{a['In_Global_Neuronal_Workspace']}\n")
    print(f"Master subnetwork annotations saved to {ann_path}")
    
    results = {}
    
    # Process each subnetwork
    for sub_name, node_indices in subnetworks.items():
        node_indices = np.array(sorted(node_indices), dtype=int)
        N_sub = len(node_indices)
        
        sub_dir = os.path.join(output_base_dir, sub_name.lower())
        os.makedirs(sub_dir, exist_ok=True)
        
        # Slice submatrices
        sub_sift = W[np.ix_(node_indices, node_indices)]
        sub_length = L[np.ix_(node_indices, node_indices)]
        
        # Network graph analysis
        adj_binary = (sub_sift > 0).astype(int)
        G = nx.from_numpy_array(adj_binary)
        components = list(nx.connected_components(G))
        gcc_size = len(max(components, key=len)) if components else 0
        
        possible_edges = N_sub * (N_sub - 1) / 2.0 if N_sub > 1 else 1.0
        actual_edges = int(np.sum(np.triu(adj_binary, k=1)))
        density = actual_edges / possible_edges if possible_edges > 0 else 0.0
        
        sub_strengths = np.sum(sub_sift, axis=1)
        
        # Save isolated CSVs
        sift_out = os.path.join(sub_dir, f"subnetwork_sift_{resolution}.csv")
        length_out = os.path.join(sub_dir, f"subnetwork_length_{resolution}.csv")
        idx_out = os.path.join(sub_dir, f"subnetwork_indices_{resolution}.csv")
        labels_out = os.path.join(sub_dir, f"subnetwork_labels_{resolution}.txt")
        stats_out = os.path.join(sub_dir, f"subnetwork_stats_{resolution}.json")
        
        np.savetxt(sift_out, sub_sift, delimiter=",", fmt="%.8f")
        np.savetxt(length_out, sub_length, delimiter=",", fmt="%.8f")
        np.savetxt(idx_out, node_indices, delimiter=",", fmt="%d")
        
        sub_labels = [labels[i] for i in node_indices]
        with open(labels_out, "w") as f:
            for l in sub_labels:
                f.write(f"{l}\n")
                
        stats = {
            "subnetwork_name": sub_name,
            "resolution": resolution,
            "num_nodes": N_sub,
            "num_edges": actual_edges,
            "density": density,
            "gcc_nodes": gcc_size,
            "is_fully_connected": bool(gcc_size == N_sub),
            "mean_internal_strength": float(np.mean(sub_strengths)),
            "median_internal_strength": float(np.median(sub_strengths)),
            "max_internal_strength": float(np.max(sub_strengths))
        }
        
        with open(stats_out, "w") as f:
            json.dump(stats, f, indent=4)
            
        results[sub_name] = stats
        print(f"Extracted {sub_name}: N={N_sub}, Edges={actual_edges}, GCC={gcc_size}/{N_sub}, Density={density:.4f}")
        
    return results
