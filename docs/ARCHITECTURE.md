# Connectome-Core Architecture & Pipeline Flow

## Overview
`connectome-core` is a high-throughput, biologically anchored neuroimaging and network analytics pipeline designed to extract robust structural connectome backbones (S-Cores) and generate exact dynamical control networks for brain simulations.

```
+-------------------------------------------------------------------------------+
|                             RAW HCP DATA ARCHIVES                             |
|          (Structural T1w Restore & Diffusion DWI Data across Cohort)          |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                     PREPROCESSING & DIFFUSION MODELING                        |
|  * Multi-Tissue Response Estimation (dwi2response dhollander: WM, GM, CSF)     |
|  * Multi-Tissue CSD & Intensity Normalization (mtnormalise: WM+GM+CSF = 1.0)  |
|  * Anatomically-Constrained Tractography (iFOD2: 10M Streamlines, Dynamic Seed)|
|  * SIFT2 Filtering: Continuous Axonal Volume Weighting & Subject Mu Extraction|
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                    PARCELLATION & CONNECTOME GENERATION                       |
|  * Schaefer 7-Network Cortical Parcellation (600, 700, 800, 900, 1000 nodes)   |
|  * FSL FIRST 14 Subcortical Nuclei Integration (614, 714, 814, 914, 1014 nodes)|
|  * tck2connectome: SIFT2 Weights, Conditional Lengths, & Streamline Counts     |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                     GROUP CONSENSUS & SIFT2 MU NORMALIZATION                  |
|  * Outlier QC: 3-Sigma Cutoff on Subject-Specific Mu Scaling Factors          |
|  * Scaling: W_AFD = W_SIFT2 * Mu (Calibrated Apparent Fiber Density)          |
|  * Robust Aggregation: Element-Wise Median Consensus (Natural >50% Prevalence)|
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                      S-CORE (STRENGTH CORE) EXTRACTION                        |
|  * Continuous Node Strength Ranking: s_i = sum_j W_ij(SIFT2)                  |
|  * Proportional Top 15% Hub Selection                                        |
|  * Giant Connected Component (GCC) Subgraph Extraction                        |
|  * Dense S-Core Submatrices Export (N_core x N_core)                          |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                       DYNAMICAL CONTROL NULL MODELS                           |
|  * control_networks/er/               : Density & Size Matched Random Graph   |
|  * control_networks/regular/          : Median-Degree Regular Graph (No Hubs) |
|  * control_networks/degree_preserved/ : Maslov-Sneppen Degree-Preserved Graph |
|  * Shuffled Empirical Core SIFT2 Weights Assigned Across All Null Topologies  |
+-------------------------------------------------------------------------------+
```

## Directory Structure
* `src/`: Modular, object-oriented core libraries for preprocessing, connectome generation, analytics, and plotting.
* `scripts/`: Production CLI entry points for batch and single-subject processing.
* `configs/`: Pipeline parameters and subcortical label lookups.
* `docs/`: In-depth methodological, architectural, and simulation documentation.
