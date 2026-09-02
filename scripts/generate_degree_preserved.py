#!/usr/bin/env python3
"""CLI Script: 3 Canonical Null Models for Isolated S-Core Submatrices"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analytics.null_models import generate_core_null_models

def main():
    parser = argparse.ArgumentParser(description="Generate ER, Regular, and Degree-Preserving null models for isolated S-Core.")
    parser.add_argument("--core-dir", required=True, help="Directory containing isolated core submatrices")
    parser.add_argument("--control-dir", required=True, help="Output directory for control_networks (er, regular, degree_preserved)")
    parser.add_argument("--resolutions", type=int, nargs="+", required=True, help="Atlas resolutions")

    args = parser.parse_args()
    generate_core_null_models(
        args.core_dir,
        args.control_dir,
        args.resolutions
    )

if __name__ == "__main__":
    main()
