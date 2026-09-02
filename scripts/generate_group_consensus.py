#!/usr/bin/env python3
"""CLI Script: Group Consensus Connectome Generation"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analytics.consensus import compute_group_consensus

def main():
    parser = argparse.ArgumentParser(description="Generate element-wise median group consensus matrices.")
    parser.add_argument("--connectomes-dir", required=True, help="Directory containing individual connectomes")
    parser.add_argument("--output-dir", required=True, help="Output directory for group consensus matrices")
    parser.add_argument("--resolutions", type=int, nargs="+", required=True, help="Resolutions to compute")
    parser.add_argument("--prefix", default="", help="Optional resolution prefix (e.g. 'cortex_subcortex_')")
    parser.add_argument("--min-streamlines", type=int, default=3, help="Minimum streamline threshold")
    parser.add_argument("--mu-sigma", type=float, default=3.0, help="Mu outlier cutoff threshold (sigma)")

    args = parser.parse_args()
    compute_group_consensus(
        args.connectomes_dir,
        args.output_dir,
        args.resolutions,
        prefix=args.prefix,
        min_streamline_count=args.min_streamlines,
        mu_sigma_threshold=args.mu_sigma
    )

if __name__ == "__main__":
    main()
