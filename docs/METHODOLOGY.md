# Publication-Ready Methodology

## 1. Diffusion MRI Preprocessing & Tractography
Diffusion MRI data were preprocessed according to Human Connectome Project (HCP) minimal preprocessing guidelines. Multi-tissue response functions for white matter (WM), gray matter (GM), and cerebrospinal fluid (CSF) were estimated using the `dhollander` algorithm. Multi-tissue constrained spherical deconvolution (MSMT-CSD) was performed, followed by multi-tissue log-domain intensity normalization (`mtnormalise`) enforcing $WM + GM + CSF = 1.0$ across the brain volume.

Whole-brain tractograms containing 10 million streamlines were generated using 2nd-order Integration over Fiber Orientation Distributions (`iFOD2`) with Anatomically-Constrained Tractography (ACT) derived from 5-tissue-type segmentation of the co-registered T1w image. Dynamic seeding was employed to achieve uniform white matter coverage.

## 2. Spherical-deconvolution Informed Filtering of Tractograms (SIFT2) & $\mu$ Normalization
To address standard tractography biases (length, curvature, and seeding biases), the SIFT2 algorithm was applied to determine a continuous scaling coefficient $w_s$ for each streamline $s$. Edge weights represent the total apparent fiber density (AFD) and axonal cross-sectional area:
$$W_{ij} = \sum_{s \in \text{edge}(i,j)} w_s$$

To make connectome weights quantitatively comparable across subjects, each subject's SIFT2 matrix was scaled by their subject-specific global proportionality factor $\mu$ ($W_{\text{AFD}} = W_{\text{SIFT2}} \times \mu$).

## 3. Parcellation Schemes
1. **Cortical Parcellations**: Schaefer 2018 7-network parcellation at 5 resolutions: 600, 700, 800, 900, and 1000 cortical parcels.
2. **Subcortical Parcellations**: FSL FIRST segmentation of 14 bilateral subcortical nuclei (Thalamus, Caudate, Putamen, Pallidum, Hippocampus, Amygdala, Accumbens) combined with cortical parcels yielding 614, 714, 814, 914, and 1014 regions.

## 4. Group Consensus
Cohort-wide quality control applied a 3-standard-deviation ($3\sigma$) cutoff on subject $\mu$ coefficients. The group connectome was computed using element-wise non-parametric medians (preserving physical units and natively enforcing $>50\%$ population prevalence).

## 5. Anatomical Strength Core (S-Core)
Brain regions were ranked by their total continuous SIFT2 node strength:
$$s_i = \sum_{j} W_{ij}^{\text{SIFT2}}$$
The top 15% highest-strength anatomical hubs were isolated, and their Giant Connected Component (GCC) was extracted into strict $N_{\text{core}} \times N_{\text{core}}$ submatrices.

## 6. Dynamical Control Null Models
Three null models were generated for the isolated S-Core submatrices:
1. **Erdős-Rényi (ER)**: Preserves node count ($N_{\text{core}}$) and edge count ($E_{\text{core}}$) with random link distribution.
2. **Regular Graph**: Homogeneous network where every node has identical median degree $k$.
3. **Degree-Preserved (Maslov-Sneppen)**: Rewires edges via double-edge swaps preserving the exact empirical degree sequence $k_i$ of every core hub.

Empirical core SIFT2 weights were shuffled and mapped to all null topologies.
