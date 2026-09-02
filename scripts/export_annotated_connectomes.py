#!/usr/bin/env python3
"""CLI Script: Master Core Annotation Exporter"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.analytics.annotations import export_annotated_connectomes

def main():
    parser = argparse.ArgumentParser(description="Export annotated connectomes with master core_node_annotations.csv.")
    parser.add_argument("--group-dir", required=True, help="Directory containing whole-brain consensus connectomes")
    parser.add_argument("--core-dir", required=True, help="Directory containing extracted group_cores")
    parser.add_argument("--out-dir", required=True, help="Output directory for annotated_connectomes")
    parser.add_argument("--resolutions", type=int, nargs="+", required=True, help="Atlas resolutions")

    args = parser.parse_args()
    export_annotated_connectomes(
        args.group_dir,
        args.core_dir,
        args.out_dir,
        args.resolutions
    )

if __name__ == "__main__":
    main()
