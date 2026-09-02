# Connectome-Core: High-Throughput Structural Connectome & S-Core Extraction Pipeline

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MRtrix3](https://img.shields.io/badge/MRtrix3-v3.0.3-orange.svg)](https://www.mrtrix.org/)
[![FSL](https://img.shields.io/badge/FSL-v6.0+-red.svg)](https://fsl.fmrib.ox.ac.uk/)

> **Connectome-Core** is an end-to-end, biologically anchored neuroimaging and graph analytics framework. It processes raw Human Connectome Project (HCP) multi-shell diffusion MRI to build multi-resolution cortical and hybrid subcortical structural connectomes, generates population-calibrated group consensus matrices via non-parametric median aggregation, isolates the **Top 15% Anatomical Strength Core (S-Core)**, and synthesizes 3 canonical dynamical control null models for whole-brain and core-isolated computational modeling.

---

## Table of Contents
1. [Repository Architecture](#repository-architecture)
2. [Scientific Rationale & Methodology](#scientific-rationale--methodology)
   - [Why the S-Core?](#why-the-s-core)
   - [SIFT2 Weights & Physical Meaning](#sift2-weights--physical-meaning)
   - [Subject-Specific Mu Normalization](#subject-specific-mu-normalization)
   - [Why Null Models are Required](#why-null-models-are-required)
3. [Parcellations & Resolution Hierarchy](#parcellations--resolution-hierarchy)
4. [Directory & Data Bundle Layout](#directory--data-bundle-layout)
5. [Installation & Setup](#installation--setup)
6. [Step-by-Step Execution Guide](#step-by-step-execution-guide)
   - [1. Single-Subject DWI & Connectome Pipeline](#1-single-subject-dwi--connectome-pipeline)
   - [2. Cohort Group Consensus & S-Core Analytics](#2-cohort-group-consensus--s-core-analytics)
7. [Dynamical Simulation Guide (Paradigms A & B)](#dynamical-simulation-guide-paradigms-a--b)
8. [Quality Control & Visualization](#quality-control--visualization)
9. [Troubleshooting & Performance](#troubleshooting--performance)
10. [Citation & Contact](#citation--contact)

---

## Repository Architecture

```
connectome-core/
├── README.md                      # Master hand-off & architecture documentation
├── LICENSE                        # MIT License
├── requirements.txt               # Python package dependencies
├── environment.yml                # Conda environment definition
├── setup.py                       # Python setup & packaging
│
├── configs/                       # Pipeline parameters & schemas
│   ├── default_config.json        # Tractography, S-Core, and null model parameters
│   └── subcortical_labels.json    # FSL FIRST 14 subcortical label lookups
│
├── src/                           # Modular Python Core Library
│   ├── preprocessing/             # Structural & DWI preprocessing
│   │   ├── hcp_extractor.py       # Selective HCP zip archive extraction
│   │   ├── subcortical_builder.py # FSL FIRST & Schaefer hybrid parcellation builder
│   │   └── dwi_processing.py      # MSMT-CSD, 5TT ACT, iFOD2 (10M), SIFT2
│   ├── connectome/                # Individual Connectome Generation
│   │   ├── builder.py             # tck2connectome execution (SIFT2, length, count)
│   │   └── qc_generator.py        # Heatmap generation and node coverage QC
│   ├── analytics/                 # Group Consensus & S-Core Analytics
│   │   ├── consensus.py           # Element-wise median consensus + 3-sigma mu QC
│   │   ├── score.py               # Top 15% S-Core continuous strength extraction + GCC
│   │   ├── annotations.py         # Master core_node_annotations.csv exporter (Is_Core: 1/0)
│   │   └── null_models.py         # Control networks (ER, Regular, Maslov-Sneppen)
│   └── visualization/             # High-Resolution Plotting
│       ├── matrix_plotter.py      # Clean white-background connectome heatmaps
│       └── degree_plotter.py      # Node degree & strength distribution visualizers
│
├── scripts/                       # Executable CLI Entry Points
│   ├── run_pipeline.sh            # End-to-end subject tractography & connectome script
│   ├── run_group_analytics.sh     # Master Group Consensus, S-Core, & Null Model runner
│   ├── generate_group_consensus.py# Standalone Group Consensus CLI
│   ├── generate_score.py          # Standalone S-Core Extraction CLI
│   ├── export_annotated_connectomes.py # Standalone Annotation Exporter CLI
│   └── generate_degree_preserved.py    # Standalone Core Null Models CLI
│
├── docs/                          # Comprehensive Scientific Documentation
│   ├── ARCHITECTURE.md            # Data flow diagrams and pipeline specifications
│   ├── METHODOLOGY.md             # Publication-ready methods for papers/theses
│   ├── SIMULATION_GUIDE.md        # Computational neuroscience simulation manual
│   └── TROUBLESHOOTING.md         # Disk management, crash recovery, multi-core scaling
│
└── tests/                         # Automated Unit Tests
    ├── test_score.py              # S-Core GCC and retention tests
    └── test_null_models.py        # ER, Regular, and Maslov-Sneppen validation
```

---

## Scientific Rationale & Methodology

### Why the S-Core?
The human brain is organized around a **Core–Periphery architecture**:
* A minority of highly connected regions (precuneus, posterior cingulate, superior frontal cortex, insula) form an anatomical hub backbone.
* Traditional binary K-Core peeling fails on dense connectomes. Instead, we rank every brain region by its **continuous SIFT2 node strength** (true anatomical bandwidth).
* Retaining the **Top 15% highest-strength regions** natively yields a fully integrated **Giant Connected Component (GCC)** across all atlas resolutions.

### SIFT2 Weights & Physical Meaning
Raw streamline counts suffer from length bias (longer tracts get fewer tracks), curvature bias, and seeding bias.
* In **SIFT2** (*Smith et al., NeuroImage 2015*), continuous scaling weights $w_s$ are assigned to each streamline such that the sum of streamline weights through any voxel matches the measured **Apparent Fiber Density (AFD)** from multi-tissue CSD.
* The SIFT2 edge weight $W_{ij} = \sum_{s \in (i,j)} w_s$ represents the **total effective axonal cross-sectional area** bridging regions $i$ and $j$.

### Subject-Specific $\mu$ Normalization
* Each subject's scan has different global scanner gain and baseline signal intensity.
* SIFT2 outputs a subject-specific proportionality constant $\mu$ (`<subject>_sift_mu.txt` $\approx 0.0022$).
* Multiplying $W_{\text{AFD}} = W_{\text{SIFT2}} \times \mu$ converts internal streamline weights into **calibrated physical units of cross-sectional area**, allowing valid comparison across all 169 subjects.
* Group aggregation uses element-wise **non-parametric median consensus**, which naturally eliminates acquisition outliers while enforcing $>50\%$ population edge consistency.

### Why Null Models are Required
To prove that brain simulation dynamics are driven by **evolved biological topology** rather than basic network statistics, we synthesize 3 canonical null models for the isolated core submatrix:
1. **Erdős-Rényi (ER) Null (`control_networks/er/`)**: Matches node count ($N$) and edge count ($E$) with random links. Proves dynamics are not a trivial byproduct of size and density.
2. **Regular Degree Null (`control_networks/regular/`)**: Forces every node to have identical median degree $k$. Proves whether degree heterogeneity (hubs) is necessary.
3. **Degree-Preserved (Maslov-Sneppen) Null (`control_networks/degree_preserved/`)**: Preserves the **exact empirical degree sequence** $k_i$ of every single hub while destroying higher-order motifs. Proves dynamics depend on specific biological wiring rules.
4. *All three null models receive shuffled empirical SIFT2 weights.*

---

## Parcellations & Resolution Hierarchy

1. **Cortical Parcellations**: Schaefer 2018 7-Network Atlas across 5 resolutions:
   * **600**, **700**, **800**, **900**, and **1000** cortical parcels.
2. **Hybrid Subcortical Parcellations**: Schaefer Cortical parcels + 14 Bilateral Subcortical Nuclei (FSL FIRST):
   * **614**, **714**, **814**, **914**, and **1014** regions.
   * *Subcortical regions (Indices $N-13$ to $N$)*: Left/Right Thalamus, Caudate, Putamen, Pallidum, Hippocampus, Amygdala, Accumbens.

---

## Directory & Data Bundle Layout

When exported, the `simulation_data_bundle.zip` contains 4 standardized subdirectories:

```
connectome-core/data/
├── group_connectomes_cortex/          # Cortical consensus matrices (600, 700, 800, 900, 1000)
├── group_connectomes_subcortical/      # Subcortical consensus matrices (614, 714, 814, 914, 1014)
├── annotated_connectomes_cortex/      # Full matrices + core_node_annotations.csv
├── annotated_connectomes_subcortical/  # Full matrices + core_node_annotations.csv
├── group_cores_cortex/                # Isolated N_core x N_core S-Core submatrices (Cortex)
├── group_cores_subcortical/           # Isolated N_core x N_core S-Core submatrices (Subcortical)
├── control_networks_cortex/           # Isolated core null models (ER, Regular, Degree-Preserved)
├── control_networks_subcortical/      # Isolated core null models (ER, Regular, Degree-Preserved)
└── individual_connectomes/
    ├── sift_mu/                       # All 169 subjects' SIFT2 mu scaling factors
    └── samples/                       # Multi-resolution CSV connectomes across sample subjects
```
└── control_networks/        # Isolated N_core x N_core Null Models
    ├── er/                  # control_er_sift_{res}.csv
    ├── regular/             # control_regular_sift_{res}.csv
    └── degree_preserved/    # control_degree_preserved_sift_{res}.csv
```

---

## Installation & Setup

### Prerequisites
* Linux OS (Ubuntu 20.04/22.04 LTS recommended)
* MRtrix3 (>= 3.0.3)
* FSL (>= 6.0.5)
* Python (>= 3.8)

### Conda Environment Setup
```bash
# Clone the repository
git clone https://github.com/Abolfazl-Alipour/connectome-core.git
cd connectome-core

# Create and activate conda environment
conda env create -f environment.yml
conda activate connectome-core

# Install package in editable development mode
pip install -e .
```

### Run Verification Unit Tests
```bash
python3 -m unittest discover -s tests
```

---

## Step-by-Step Execution Guide

### 1. Single-Subject DWI & Connectome Pipeline
To process an individual subject from raw HCP archives:
```bash
bash scripts/run_pipeline.sh <SUBJECT_ID> 24
```
* Uses temporary scratch directory (`tmp_work_<SUBJECT_ID>/`) with guaranteed cleanup on completion.
* Outputs individual connectomes for all 10 parcellation resolutions into `connectomes/`.

### 2. Cohort Group Consensus & S-Core Analytics
To run group median consensus, S-Core extraction, and null model generation across the entire cohort:
```bash
bash scripts/run_group_analytics.sh
```

Or execute individual stages via standalone Python CLI tools:

```bash
# 1. Group Consensus (3-sigma mu filtering + element-wise median)
python3 scripts/generate_group_consensus.py \
  --connectomes-dir connectomes/cortex_subcortex \
  --output-dir group_connectomes/cortex_subcortex \
  --resolutions 614 714 814 914 1014

# 2. Extract Top 15% S-Core Submatrices
python3 scripts/generate_score.py \
  --in-dir group_connectomes/cortex_subcortex \
  --out-dir group_cores/cortex_subcortex \
  --resolutions 614 714 814 914 1014 \
  --retention-percentage 0.15

# 3. Export Master Annotation Mapping (Is_Core: 1/0)
python3 scripts/export_annotated_connectomes.py \
  --group-dir group_connectomes/cortex_subcortex \
  --core-dir group_cores/cortex_subcortex \
  --out-dir annotated_connectomes/cortex_subcortex \
  --resolutions 614 714 814 914 1014

# 4. Generate 3 Control Null Models for Isolated Core Submatrices
python3 scripts/generate_degree_preserved.py \
  --core-dir group_cores/cortex_subcortex \
  --control-dir control_networks/cortex_subcortex \
  --resolutions 614 714 814 914 1014
```

---

## Dynamical Simulation Guide (Paradigms A & B)

```
                       +-----------------------------------+
                       |      WHICH SIMULATION PARADIGM?   |
                       +-----------------------------------+
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
+-----------------------------------+   +-----------------------------------+
|      PARADIGM A: INTACT BRAIN     |   |    PARADIGM B: ISOLATED S-CORE    |
|   (Core as Dynamical Ignition)    |   |  (Intrinsic Computational Engine) |
+-----------------------------------+   +-----------------------------------+
| * Matrix: annotated_connectomes/  |   | * Empirical Core: group_cores/    |
|   group_mean_sift_{res}.csv       |   |   core_sift_{res}.csv             |
| * Annotations:                    |   | * Null Controls: control_networks/|
|   core_node_annotations.csv       |   |   - er/                           |
| * Delays:                         |   |   - regular/                      |
|   group_mean_length_{res}.csv     |   |   - degree_preserved/             |
+-----------------------------------+   +-----------------------------------+
```

### Python Loading Example:
```python
import numpy as np
import pandas as pd

# Paradigm A: Intact Whole-Brain
W_full = np.loadtxt("annotated_connectomes/cortex_subcortex/group_mean_sift_1014.csv", delimiter=",")
L_full = np.loadtxt("annotated_connectomes/cortex_subcortex/group_mean_length_1014.csv", delimiter=",")
annotations = pd.read_csv("annotated_connectomes/cortex_subcortex/core_node_annotations.csv")
core_mask = (annotations[annotations['Resolution'] == 1014]['Is_Core'] == 1).values

# Paradigm B: Isolated S-Core vs. Degree-Preserved Null
W_core = np.loadtxt("group_cores/cortex_subcortex/core_sift_1014.csv", delimiter=",")
L_core = np.loadtxt("group_cores/cortex_subcortex/core_length_1014.csv", delimiter=",")
W_null_dp = np.loadtxt("control_networks/cortex_subcortex/degree_preserved/control_degree_preserved_sift_1014.csv", delimiter=",")
```

---

## Quality Control & Visualization

All matrix heatmaps follow high-contrast scientific standards:
* **Background**: Clean white background (`facecolor='white'`).
* **Subcortical Demarcation**: Placed on top of the axes to eliminate cell overlap.
* **Scale**: Logarithmic dynamic range ($\log_{10}(\text{SIFT2 Weight})$).

To render QC heatmaps:
```python
from src.visualization.matrix_plotter import plot_consensus_matrix
import numpy as np

mat = np.loadtxt("group_connectomes/cortex_subcortex/group_mean_sift_1014.csv", delimiter=",")
plot_consensus_matrix(mat, "qc_matrix_1014.png", "Consensus Connectome (N=1014)", subcortical_count=14)
```

---

## Troubleshooting & Performance

1. **Scratch Space**: Always keep at least 30 GB free in the temporary working partition during single-subject runs.
2. **Multi-threading**: Allocating 20–30 CPU threads to 1 subject sequentially yields faster throughput and prevents memory thrashing compared to running parallel low-core subjects.
3. **Double-Edge Swaps**: If double-edge swapping encounters high density on small test graphs, the algorithm automatically adjusts swap counts and falls back to degree sequence configuration generators.

---

## Citation & Contact

If you use this pipeline or data bundles in your research, please cite:
* **Smith et al.** (2015). *SIFT2: Enabling dense quantitative assessment of brain white matter connectivity.* NeuroImage, 119, 338-351.
* **Schaefer et al.** (2018). *Local-Global Parcellation of the Human Cerebral Cortex from Intrinsic Functional Connectivity MRI.* Cerebral Cortex, 28(9), 3095-3114.
* **Alipour, A.** (2026). *Structural Connectome Core Extraction Pipeline across Multi-Resolution Cortical and Subcortical Atlases.*

**Author**: Abolfazl (Reza) Alipour  
**GitHub**: [@Abolfazl-Alipour](https://github.com/Abolfazl-Alipour)  
**Repository**: [connectome-core](https://github.com/Abolfazl-Alipour/connectome-core)
