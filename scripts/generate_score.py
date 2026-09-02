#!/usr/bin/env python3
"""CLI Script: S-Core (Top 15% Anatomical Strength Core) Extraction"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analytics.score import extract_score

def main():
    parser = argparse.ArgumentParser(description="Extract S-Core submatrices from group consensus connectomes.")
    parser.add_argument("--in-dir", required=True, help="Directory containing group consensus matrices")
    parser.add_argument("--out-dir", required=True, help="Output directory for group_cores submatrices")
    parser.add_argument("--resolutions", type=int, nargs="+", required=True, help="Atlas resolutions")
    parser.add_argument("--retention-percentage", type=float, default=0.15, help="Proportional retention (default: 0.15)")

    args = parser.parse_args()
    extract_score(
        args.in_dir,
        args.out_dir,
        args.resolutions,
        retention_percentage=args.retention_percentage
    )

if __name__ == "__main__":
    main()
