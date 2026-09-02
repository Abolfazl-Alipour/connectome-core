# Dynamical Simulation & Modeling Guide

This guide is intended for computational neuroscientists and collaborators conducting neural mass, oscillator, or firing rate simulations (e.g. Kuramoto, Wilson-Cowan, Jansen-Rit, FitzHugh-Nagumo) using the `connectome-core` bundle.

---

## 1. Bundle Directory Structure

```
simulation_data_bundle/
├── group_connectomes/       # Full N x N consensus matrices
│   ├── group_mean_sift_{res}.csv
│   ├── group_mean_length_{res}.csv
│   └── group_prevalence_{res}.csv
│
├── annotated_connectomes/   # Full N x N matrices + Core Annotation Mapping
│   ├── group_mean_sift_{res}.csv
│   ├── group_mean_length_{res}.csv
│   ├── group_prevalence_{res}.csv
│   └── core_node_annotations.csv
│
├── group_cores/             # Dense N_core x N_core S-Core Submatrices (Top 15% Hubs)
│   ├── core_sift_{res}.csv
│   ├── core_length_{res}.csv
│   ├── core_prevalence_{res}.csv
│   ├── core_node_indices_{res}.csv
│   └── core_stats_{res}.json
│
└── control_networks/        # Dense N_core x N_core Null Models
    ├── er/                  # Erdős-Rényi Random Networks
    ├── regular/             # Uniform Median-Degree Networks
    └── degree_preserved/    # Maslov-Sneppen Degree-Preserved Networks
```

---

## 2. Simulation Paradigms

### Paradigm A: Intact Whole-Brain Core Ignition
* **Goal**: Test whether the core acts as an ignition switch driving peripheral brain dynamics.
* **Matrices**: Load `annotated_connectomes/group_mean_sift_{res}.csv` and `group_mean_length_{res}.csv`.
* **Node Partitioning**: Read `annotated_connectomes/core_node_annotations.csv` to identify `Is_Core == 1` vs `Is_Core == 0`.
* **Protocols**:
  1. *Core Perturbation*: Drive core nodes with rhythmic input; observe information transmission to the periphery.
  2. *Core Lesioning*: Set core-to-periphery connection weights to zero; measure degradation of whole-brain synchronization and metastability.

### Paradigm B: Isolated S-Core Computational Capacity
* **Goal**: Test whether the core network intrinsically sustains critical, complex dynamical states on its own.
* **Empirical Core Simulation**: Run oscillator dynamics on `group_cores/core_sift_{res}.csv` with time delays from `group_cores/core_length_{res}.csv`.
* **Hypothesis Testing via Null Controls**:
  - Run identical simulation on `control_networks/er/control_er_sift_{res}.csv` (tests if density/size is sufficient).
  - Run identical simulation on `control_networks/regular/control_regular_sift_{res}.csv` (tests if degree heterogeneity/hubs are necessary).
  - Run identical simulation on `control_networks/degree_preserved/control_degree_preserved_sift_{res}.csv` (tests if higher-order biological wiring motifs are necessary).

---

## 3. Conduction Velocity & Time Delays
To incorporate conduction delays $\tau_{ij}$ into neural differential equations:
$$\tau_{ij} = \frac{L_{ij}}{v}$$
where:
* $L_{ij}$ is the tract length in millimeters from `*_length_{res}.csv`.
* $v$ is the axonal conduction velocity (standard empirical range: $1.5 - 10.0\text{ m/s}$).
