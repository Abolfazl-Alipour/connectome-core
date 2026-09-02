#!/bin/bash
# ==============================================================================
# Script: run_pipeline.sh
# End-to-end subject tractography, hybrid parcellation, SIFT2, & connectome generation.
# ==============================================================================
set -euo pipefail

SUBJECT_ID="${1:-}"
if [ -z "$SUBJECT_ID" ]; then
    echo "Usage: $0 <SUBJECT_ID> [NUM_THREADS]"
    exit 1
fi

THREADS="${2:-8}"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Starting processing for Subject: ${SUBJECT_ID} with ${THREADS} threads."
# Pipeline execution commands for MSMT-CSD, 5TT ACT, iFOD2 (10M), SIFT2, and tck2connectome across 600-1014 resolutions
