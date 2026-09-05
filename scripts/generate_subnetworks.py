#!/usr/bin/env python3
"""
CLI Script: generate_subnetworks.py
Extracts isolated submatrices and node mappings for the 7 canonical Yeo networks
and the 2 consciousness subgraphs (Posterior Cortical Hot Zone and Global Neuronal Workspace).
"""

import os
import sys
import argparse

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analytics.subnetworks import extract_subnetwork_matrices

def main():
    parser = argparse.ArgumentParser(description="Extract canonical subnetworks and consciousness subgraphs.")
    parser.add_argument(
        "--sift-path",
        type=str,
        default="data/group_connectomes_cortex/group_mean_sift_1000.csv",
        help="Path to SIFT2 consensus matrix (CSV)"
    )
    parser.add_argument(
        "--length-path",
        type=str,
        default="data/group_connectomes_cortex/group_mean_length_1000.csv",
        help="Path to tract length consensus matrix (CSV)"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="data/subnetworks",
        help="Output directory for extracted subnetworks"
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=1000,
        help="Schaefer atlas cortical resolution (default: 1000)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.sift_path):
        print(f"Error: SIFT matrix not found at {args.sift_path}")
        sys.exit(1)
        
    print(f"=== Extracting Subnetworks for Resolution {args.resolution} ===")
    print(f"  SIFT Input  : {args.sift_path}")
    print(f"  Length Input: {args.length_path}")
    print(f"  Output Dir  : {args.out_dir}")
    
    results = extract_subnetwork_matrices(
        sift_matrix_path=args.sift_path,
        length_matrix_path=args.length_path,
        output_base_dir=args.out_dir,
        resolution=args.resolution
    )
    
    print("\n=== Subnetwork Extraction Summary ===")
    for name, stats in results.items():
        conn_str = "Fully Connected" if stats['is_fully_connected'] else f"GCC: {stats['gcc_nodes']}/{stats['num_nodes']}"
        print(f"  * {name:<28}: N={stats['num_nodes']:>4} nodes, E={stats['num_edges']:>5} edges, Density={stats['density']:.4f}, Status: {conn_str}")
        
    print("\nProcessing completed successfully.")

if __name__ == "__main__":
    main()
