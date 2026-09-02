#!/bin/bash
# ==============================================================================
# Pipeline: run_group_analytics.sh
# End-to-end execution of Group Consensus, S-Core (Top 15%), Annotation Mapping,
# and 3 Control Null Models for both Cortex and Cortex+Subcortex datasets.
# ==============================================================================
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="python3"

echo "=================================================="
echo "Starting Master Connectome Core Analytics Pipeline"
echo "Base Directory: ${BASE_DIR}"
echo "Start Time: $(date)"
echo "=================================================="

# 1. Cortex-Only Analytics (600, 700, 800, 900, 1000)
echo -e "\n[Step 1/2] Processing Cortical Group Analytics (600-1000)..."
${PYTHON} "${BASE_DIR}/scripts/generate_group_consensus.py" \
  --connectomes-dir "${BASE_DIR}/connectomes/cortex_only" \
  --output-dir "${BASE_DIR}/group_connectomes/cortex_only" \
  --resolutions 600 700 800 900 1000

${PYTHON} "${BASE_DIR}/scripts/generate_score.py" \
  --in-dir "${BASE_DIR}/group_connectomes/cortex_only" \
  --out-dir "${BASE_DIR}/group_cores/cortex_only" \
  --resolutions 600 700 800 900 1000

${PYTHON} "${BASE_DIR}/scripts/export_annotated_connectomes.py" \
  --group-dir "${BASE_DIR}/group_connectomes/cortex_only" \
  --core-dir "${BASE_DIR}/group_cores/cortex_only" \
  --out-dir "${BASE_DIR}/annotated_connectomes/cortex_only" \
  --resolutions 600 700 800 900 1000

${PYTHON} "${BASE_DIR}/scripts/generate_degree_preserved.py" \
  --core-dir "${BASE_DIR}/group_cores/cortex_only" \
  --control-dir "${BASE_DIR}/control_networks/cortex_only" \
  --resolutions 600 700 800 900 1000

# 2. Cortex+Subcortex Analytics (614, 714, 814, 914, 1014)
echo -e "\n[Step 2/2] Processing Subcortical Group Analytics (614-1014)..."
${PYTHON} "${BASE_DIR}/scripts/generate_group_consensus.py" \
  --connectomes-dir "${BASE_DIR}/connectomes/cortex_subcortex" \
  --output-dir "${BASE_DIR}/group_connectomes/cortex_subcortex" \
  --resolutions 614 714 814 914 1014

${PYTHON} "${BASE_DIR}/scripts/generate_score.py" \
  --in-dir "${BASE_DIR}/group_connectomes/cortex_subcortex" \
  --out-dir "${BASE_DIR}/group_cores/cortex_subcortex" \
  --resolutions 614 714 814 914 1014

${PYTHON} "${BASE_DIR}/scripts/export_annotated_connectomes.py" \
  --group-dir "${BASE_DIR}/group_connectomes/cortex_subcortex" \
  --core-dir "${BASE_DIR}/group_cores/cortex_subcortex" \
  --out-dir "${BASE_DIR}/annotated_connectomes/cortex_subcortex" \
  --resolutions 614 714 814 914 1014

${PYTHON} "${BASE_DIR}/scripts/generate_degree_preserved.py" \
  --core-dir "${BASE_DIR}/group_cores/cortex_subcortex" \
  --control-dir "${BASE_DIR}/control_networks/cortex_subcortex" \
  --resolutions 614 714 814 914 1014

echo -e "\n=================================================="
echo "Master Group Analytics Pipeline Completed Successfully!"
echo "End Time: $(date)"
echo "=================================================="
