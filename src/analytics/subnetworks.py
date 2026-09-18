"""
Module: subnetworks
Extracts canonical functional subnetworks (Yeo 7) and consciousness-relevant
subgraphs (Posterior Cortical Hot Zone and Global Neuronal Workspace) from
multi-resolution Schaefer 2018 structural connectomes, with full support for
hybrid cortical-subcortical resolutions (e.g. 1014 nodes).
"""

import os
import json
import re
import csv
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

SUBCORTICAL_STRUCTURES = [
    {"offset": 1, "name": "Left-Thalamus-Proper", "fsl_label": 10, "hemi": "Left", "region": "Thalamus"},
    {"offset": 2, "name": "Left-Caudate", "fsl_label": 11, "hemi": "Left", "region": "Caudate"},
    {"offset": 3, "name": "Left-Putamen", "fsl_label": 12, "hemi": "Left", "region": "Putamen"},
    {"offset": 4, "name": "Left-Pallidum", "fsl_label": 13, "hemi": "Left", "region": "Pallidum"},
    {"offset": 5, "name": "Left-Hippocampus", "fsl_label": 17, "hemi": "Left", "region": "Hippocampus"},
    {"offset": 6, "name": "Left-Amygdala", "fsl_label": 18, "hemi": "Left", "region": "Amygdala"},
    {"offset": 7, "name": "Left-Accumbens-area", "fsl_label": 26, "hemi": "Left", "region": "Accumbens"},
    {"offset": 8, "name": "Right-Thalamus-Proper", "fsl_label": 49, "hemi": "Right", "region": "Thalamus"},
    {"offset": 9, "name": "Right-Caudate", "fsl_label": 50, "hemi": "Right", "region": "Caudate"},
    {"offset": 10, "name": "Right-Putamen", "fsl_label": 51, "hemi": "Right", "region": "Putamen"},
    {"offset": 11, "name": "Right-Pallidum", "fsl_label": 52, "hemi": "Right", "region": "Pallidum"},
    {"offset": 12, "name": "Right-Hippocampus", "fsl_label": 53, "hemi": "Right", "region": "Hippocampus"},
    {"offset": 13, "name": "Right-Amygdala", "fsl_label": 54, "hemi": "Right", "region": "Amygdala"},
    {"offset": 14, "name": "Right-Accumbens-area", "fsl_label": 58, "hemi": "Right", "region": "Accumbens"}
]

def get_schaefer_labels(res: int) -> List[str]:
    """Fetches official Schaefer 2018 7-Networks parcel labels for a given resolution."""
    atlas = nilearn.datasets.fetch_atlas_schaefer_2018(n_rois=res, yeo_networks=7)
    raw_labels = atlas.labels[1:]
    labels = [l.decode('utf-8') if isinstance(l, bytes) else str(l) for l in raw_labels]
    if len(labels) != res:
        raise ValueError(f"Expected {res} labels for Schaefer atlas, got {len(labels)}")
    return labels

def classify_yeo_network(label: str) -> str:
    """Classifies a Schaefer cortical label into one of the canonical 7 Yeo networks."""
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
    elif "Subcortex" in label or any(s["name"] in label for s in SUBCORTICAL_STRUCTURES):
        return "Subcortex"
    else:
        raise ValueError(f"Unrecognized network in label: {label}")

def is_posterior_hot_zone(label: str) -> bool:
    """
    Identifies if a parcel belongs to the Posterior Cortical Hot Zone (IIT / Koch & Tononi).
    Encompasses parietal, occipital, and temporal sensory/associative regions,
    explicitly excluding the prefrontal cortex.
    """
    if "_Vis_" in label:
        return True
    if "_DorsAttn_Post_" in label:
        return True
    if "_Cont_Par_" in label or "_Cont_pCun_" in label:
        return True
    if any(k in label for k in ["_Default_pCunPCC_", "_Default_Par_", "_Default_Temp_", "_Default_PHC_"]):
        return True
    if any(k in label for k in ["_SalVentAttn_TempOcc", "_SalVentAttn_ParOper"]):
        return True
    return False

def is_global_neuronal_workspace(label: str) -> bool:
    """
    Identifies if a parcel belongs to the Global Neuronal Workspace (GNWT / Stanislas Dehaene).
    Encompasses the frontoparietal control network, salience/ventral attention,
    and prefrontal projection hubs.
    """
    if "_Cont_" in label:
        return True
    if "_SalVentAttn_" in label:
        return True
    if any(k in label for k in ["_Default_PFC_", "_Default_PFCdPFCm_", "_Default_PFCv_"]):
        return True
    if "_DorsAttn_FEF_" in label:
        return True
    return False

def build_hybrid_node_metadata(resolution: int) -> Tuple[List[str], List[Dict]]:
    """
    Constructs full metadata for each node in a cortical or hybrid resolution.
    Returns (labels_list, metadata_dict_list).
    """
    is_hybrid = (resolution > 1000 and resolution % 100 == 14) or (resolution in [614, 714, 814, 914, 1014])
    cortex_count = resolution - 14 if is_hybrid else resolution
    
    cortical_labels = get_schaefer_labels(cortex_count)
    labels = list(cortical_labels)
    metadata = []
    
    for idx, cl in enumerate(cortical_labels):
        parts = cl.split("_")
        hemi_str = "Left" if parts[1] == "LH" else "Right"
        net = classify_yeo_network(cl)
        subreg = parts[3] if len(parts) > 4 else parts[2]
        
        metadata.append({
            "Node_Index_0based": idx,
            "Node_Index_1based": idx + 1,
            "Parcel_Label": cl,
            "Structure_Type": "Cortex",
            "Hemisphere": hemi_str,
            "Anatomical_Region": subreg,
            "Yeo_Network": net,
            "FSL_Label": -1,
            "In_Posterior_Hot_Zone": int(is_posterior_hot_zone(cl)),
            "In_Global_Neuronal_Workspace": int(is_global_neuronal_workspace(cl))
        })
        
    if is_hybrid:
        for s_idx, struct in enumerate(SUBCORTICAL_STRUCTURES):
            global_idx = cortex_count + s_idx
            label_name = f"Subcortex_{struct['name']}"
            labels.append(label_name)
            
            metadata.append({
                "Node_Index_0based": global_idx,
                "Node_Index_1based": global_idx + 1,
                "Parcel_Label": label_name,
                "Structure_Type": "Subcortex",
                "Hemisphere": struct["hemi"],
                "Anatomical_Region": struct["region"],
                "Yeo_Network": "Subcortex",
                "FSL_Label": struct["fsl_label"],
                "In_Posterior_Hot_Zone": 0,
                "In_Global_Neuronal_Workspace": 0
            })
            
    return labels, metadata

def export_master_labels_file(metadata: List[Dict], out_csv_path: str):
    """Exports a clean master CSV listing Node ID, Label, Structure, Hemisphere, Region, Network."""
    os.makedirs(os.path.dirname(os.path.abspath(out_csv_path)), exist_ok=True)
    fieldnames = [
        "Node_Index_0based",
        "Node_Index_1based",
        "Parcel_Label",
        "Structure_Type",
        "Hemisphere",
        "Anatomical_Region",
        "Yeo_Network",
        "FSL_Label",
        "In_Posterior_Hot_Zone",
        "In_Global_Neuronal_Workspace"
    ]
    with open(out_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in metadata:
            writer.writerow(row)
    print(f"Master node label reference exported to: {out_csv_path}")

def extract_subnetwork_matrices(
    sift_matrix_path: str,
    length_matrix_path: str,
    output_base_dir: str,
    resolution: int = 1000,
    include_subcortical_augmented: bool = True
) -> Dict[str, Dict]:
    """
    Extracts isolated submatrices, index mappings, and summary statistics
    for all 7 Yeo networks, consciousness subgraphs, and their subcortical-augmented versions.
    """
    os.makedirs(output_base_dir, exist_ok=True)
    
    labels, metadata = build_hybrid_node_metadata(resolution)
    
    W = np.loadtxt(sift_matrix_path, delimiter=",")
    L = np.loadtxt(length_matrix_path, delimiter=",") if os.path.exists(length_matrix_path) else np.zeros_like(W)
    
    W = (W + W.T) / 2.0
    np.fill_diagonal(W, 0.0)
    L = (L + L.T) / 2.0
    np.fill_diagonal(L, 0.0)
    
    if W.shape[0] != resolution:
        raise ValueError(f"Matrix dimension {W.shape[0]} does not match resolution {resolution}")
        
    # Export master labels file
    labels_csv = os.path.join(output_base_dir, f"node_labels_{resolution}.csv")
    export_master_labels_file(metadata, labels_csv)
    
    is_hybrid = (resolution > 1000 and resolution % 100 == 14) or (resolution in [614, 714, 814, 914, 1014])
    cortex_count = resolution - 14 if is_hybrid else resolution
    subcortical_indices = list(range(cortex_count, resolution)) if is_hybrid else []
    
    # 1. Base Cortical Subnetworks
    subnetworks = {net: [] for net in YEO_7_NETWORKS}
    subnetworks["Posterior_Hot_Zone"] = []
    subnetworks["Global_Neuronal_Workspace"] = []
    
    for row in metadata[:cortex_count]:
        idx = row["Node_Index_0based"]
        net = row["Yeo_Network"]
        subnetworks[net].append(idx)
        if row["In_Posterior_Hot_Zone"]:
            subnetworks["Posterior_Hot_Zone"].append(idx)
        if row["In_Global_Neuronal_Workspace"]:
            subnetworks["Global_Neuronal_Workspace"].append(idx)
            
    # 2. Add Subcortical-Included Versions if available
    augmented_subnetworks = {}
    if is_hybrid and include_subcortical_augmented:
        for net_name, c_indices in subnetworks.items():
            aug_name = f"{net_name}_with_subcortex"
            augmented_subnetworks[aug_name] = c_indices + subcortical_indices
            
        augmented_subnetworks["Subcortex_Only"] = subcortical_indices
        
    all_targets = {**subnetworks, **augmented_subnetworks}
    results = {}
    
    # Process each subnetwork
    for sub_name, node_indices in all_targets.items():
        node_indices = np.array(sorted(node_indices), dtype=int)
        N_sub = len(node_indices)
        
        sub_dir = os.path.join(output_base_dir, sub_name.lower())
        os.makedirs(sub_dir, exist_ok=True)
        
        sub_sift = W[np.ix_(node_indices, node_indices)]
        sub_length = L[np.ix_(node_indices, node_indices)]
        
        adj_binary = (sub_sift > 0).astype(int)
        G = nx.from_numpy_array(adj_binary)
        components = list(nx.connected_components(G))
        gcc_size = len(max(components, key=len)) if components else 0
        
        possible_edges = N_sub * (N_sub - 1) / 2.0 if N_sub > 1 else 1.0
        actual_edges = int(np.sum(np.triu(adj_binary, k=1)))
        density = actual_edges / possible_edges if possible_edges > 0 else 0.0
        
        sub_strengths = np.sum(sub_sift, axis=1)
        
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
        print(f"Extracted {sub_name:<38}: N={N_sub:>4}, Edges={actual_edges:>6}, GCC={gcc_size}/{N_sub}, Density={density:.4f}")
        
    return results
